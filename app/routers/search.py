"""Node and edge search endpoints.

Endpoints:
- GET /api/{database}/search/node/full - Search nodes with fuzzy matching
- GET /api/{database}/search/edge/full - Search relationships with fuzzy matching
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import JSONResponse
from neo4j.exceptions import ClientError

from app.dependencies import verify_api_key
from app.models import Error, ErrorResponse, SearchResponse, SearchResult

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/{database}/search",
    tags=["search"],
)


@router.get(
    "/node/full",
    response_model=SearchResponse,
    responses={
        200: {"model": SearchResponse, "description": "Search successful"},
        403: {"description": "Authentication failed"},
        404: {"description": "Database not found"},
        422: {"description": "Validation error"},
        503: {"description": "Neo4j unavailable"},
    },
)
async def search_nodes(
    request: Request,
    database: str = Path(..., description="Target database name"),
    q: str = Query(..., min_length=1, description="Search query"),
    _fuzziness: float = Query(
        0.7,
        ge=0.0,
        le=1.0,
        alias="fuzziness",
        description="Fuzzy matching tolerance (0-1)",
    ),
    size: int = Query(20, ge=1, le=1000, description="Maximum results"),
    from_param: int = Query(0, ge=0, alias="from", description="Pagination offset"),
    _: None = Depends(verify_api_key),
) -> SearchResponse | JSONResponse:
    """Search for nodes with fuzzy matching on properties.

    Performs case-insensitive substring matching across all node properties.
    The fuzziness parameter is accepted for future compatibility but not
    currently used (v1.0.0 uses CONTAINS matching).

    Args:
        request: FastAPI request object.
        database: Target database name from path.
        q: Search query string.
        _fuzziness: Fuzzy matching tolerance (0.0-1.0, not used in v1.0).
        size: Maximum number of results to return.
        from_param: Offset for pagination.
        _: API key verification dependency.

    Returns:
        SearchResponse with matching nodes.
    """
    # Check if Neo4j client is available
    neo4j_client = getattr(request.app.state, "neo4j_client", None)
    if neo4j_client is None:
        logger.warning("Neo4j client not available for search")
        error_response = ErrorResponse(
            error=Error(
                code="NEO4J_UNAVAILABLE",
                message="Neo4j database is not available",
            )
        )
        return JSONResponse(status_code=503, content=error_response.model_dump())

    # Cypher query with case-insensitive CONTAINS matching
    # Note: fuzziness parameter is accepted but not used in v1.0.0
    query = """
    MATCH (n)
    WHERE ANY(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($q))
    RETURN n
    SKIP $from_param
    LIMIT $size
    """

    try:
        results = neo4j_client.execute_query(
            query=query,
            parameters={"q": q, "from_param": from_param, "size": size},
            database=database,
        )

        # Convert Neo4j nodes to SearchResult format
        search_results = [
            SearchResult(
                id=str(record["n"].element_id),
                labels=list(record["n"].labels),
                properties=dict(record["n"].items()),
            )
            for record in results
        ]

        # Determine if more results might exist
        more_results = len(search_results) == size

        # totalHits: 0 if no results (we know the exact count),
        # None otherwise (unknown without separate COUNT query)
        total_hits = 0 if len(search_results) == 0 else None

        return SearchResponse(  # type: ignore[call-arg]
            type="node",
            total_hits=total_hits,
            more_results=more_results,
            results=search_results,
        )

    except ClientError as e:
        # Check for database not found using Neo4j error code
        if getattr(e, "code", None) == "Neo.ClientError.Database.DatabaseNotFound":
            logger.warning("Database not found: %s", database)
            error_response = ErrorResponse(
                error=Error(
                    code="DATABASE_NOT_FOUND",
                    message=f"Database '{database}' not found",
                    details={"database": database},
                )
            )
            return JSONResponse(status_code=404, content=error_response.model_dump())
        # Re-raise unexpected errors
        raise


@router.get(
    "/edge/full",
    response_model=SearchResponse,
    responses={
        200: {"model": SearchResponse, "description": "Search successful"},
        403: {"description": "Authentication failed"},
        404: {"description": "Database not found"},
        422: {"description": "Validation error"},
        503: {"description": "Neo4j unavailable"},
    },
)
async def search_edges(
    request: Request,
    database: str = Path(..., description="Target database name"),
    q: str = Query(..., min_length=1, description="Search query"),
    _fuzziness: float = Query(
        0.7,
        ge=0.0,
        le=1.0,
        alias="fuzziness",
        description="Fuzzy matching tolerance (0-1)",
    ),
    size: int = Query(20, ge=1, le=1000, description="Maximum results"),
    from_param: int = Query(0, ge=0, alias="from", description="Pagination offset"),
    _: None = Depends(verify_api_key),
) -> SearchResponse | JSONResponse:
    """Search for edges/relationships with fuzzy matching on properties.

    Performs case-insensitive substring matching across all relationship properties.
    The fuzziness parameter is accepted for future compatibility but not
    currently used (v1.0.0 uses CONTAINS matching).

    Args:
        request: FastAPI request object.
        database: Target database name from path.
        q: Search query string.
        _fuzziness: Fuzzy matching tolerance (0.0-1.0, not used in v1.0).
        size: Maximum number of results to return.
        from_param: Offset for pagination.
        _: API key verification dependency.

    Returns:
        SearchResponse with matching edges.
    """
    # Check if Neo4j client is available
    neo4j_client = getattr(request.app.state, "neo4j_client", None)
    if neo4j_client is None:
        logger.warning("Neo4j client not available for edge search")
        error_response = ErrorResponse(
            error=Error(
                code="NEO4J_UNAVAILABLE",
                message="Neo4j database is not available",
            )
        )
        return JSONResponse(status_code=503, content=error_response.model_dump())

    # Cypher query with case-insensitive CONTAINS matching for relationships
    # Note: fuzziness parameter is accepted but not used in v1.0.0
    query = """
    MATCH ()-[r]-()
    WHERE ANY(prop IN keys(r) WHERE toLower(toString(r[prop])) CONTAINS toLower($q))
    RETURN r, startNode(r) as source, endNode(r) as target
    SKIP $from_param
    LIMIT $size
    """

    try:
        results = neo4j_client.execute_query(
            query=query,
            parameters={"q": q, "from_param": from_param, "size": size},
            database=database,
        )

        # Convert Neo4j relationships to SearchResult format
        search_results = [
            SearchResult(
                id=str(record["r"].element_id),
                type=record["r"].type,
                source=str(record["source"].element_id),
                target=str(record["target"].element_id),
                properties=dict(record["r"].items()),
            )
            for record in results
        ]

        # Determine if more results might exist
        more_results = len(search_results) == size

        # totalHits: 0 if no results (we know the exact count),
        # None otherwise (unknown without separate COUNT query)
        total_hits = 0 if len(search_results) == 0 else None

        return SearchResponse(  # type: ignore[call-arg]
            type="edge",
            total_hits=total_hits,
            more_results=more_results,
            results=search_results,
        )

    except ClientError as e:
        # Check for database not found using Neo4j error code
        if getattr(e, "code", None) == "Neo.ClientError.Database.DatabaseNotFound":
            logger.warning("Database not found: %s", database)
            error_response = ErrorResponse(
                error=Error(
                    code="DATABASE_NOT_FOUND",
                    message=f"Database '{database}' not found",
                    details={"database": database},
                )
            )
            return JSONResponse(status_code=404, content=error_response.model_dump())
        # Re-raise unexpected errors
        raise
