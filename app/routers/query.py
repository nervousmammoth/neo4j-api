"""Cypher query execution endpoint.

Endpoints:
- POST /api/{database}/graph/query - Execute read-only Cypher queries
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse
from neo4j.exceptions import ClientError, Neo4jError
from neo4j.graph import Node as Neo4jNode
from neo4j.graph import Relationship as Neo4jRelationship

from app.config import get_settings
from app.dependencies import verify_api_key
from app.models import (
    Edge,
    EdgeData,
    Error,
    ErrorResponse,
    Node,
    NodeData,
    QueryMeta,
    QueryRequest,
    QueryResponse,
)
from app.utils.validators import get_forbidden_keyword, is_read_only_query

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/{database}/graph",
    tags=["query"],
)

# Allowed read operations for error message
ALLOWED_OPERATIONS = [
    "MATCH",
    "RETURN",
    "WITH",
    "WHERE",
    "ORDER BY",
    "LIMIT",
    "SKIP",
    "CALL",
    "SHOW",
    "UNWIND",
    "OPTIONAL MATCH",
]


def _truncate_query(query: str, max_length: int = 100) -> str:
    """Truncate a query string for inclusion in error responses.

    Args:
        query: The query string to truncate.
        max_length: Maximum length before truncation.

    Returns:
        The original query if <= max_length, otherwise truncated with indicator.
    """
    if len(query) <= max_length:
        return query
    return query[:max_length] + "... [truncated]"


def _extract_error_position(error_msg: str) -> int | None:
    """Extract column position from Neo4j error message.

    Args:
        error_msg: The error message from Neo4j.

    Returns:
        The column position if found, None otherwise.
    """
    # Pattern: "(line X, column Y)" or "position Y"
    match = re.search(r"column\s+(\d+)|position\s+(\d+)", error_msg, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    return None


def _convert_neo4j_node(node: Neo4jNode) -> Node:
    """Convert a Neo4j Node to Linkurious format.

    Args:
        node: Neo4j node object.

    Returns:
        Node in Linkurious format.
    """
    return Node(
        id=str(node.element_id),
        data=NodeData(
            categories=list(node.labels),
            properties=dict(node.items()),
        ),
    )


def _convert_neo4j_relationship(rel: Neo4jRelationship) -> Edge | None:
    """Convert a Neo4j Relationship to Linkurious format.

    Args:
        rel: Neo4j relationship object.

    Returns:
        Edge in Linkurious format, or None if start/end nodes are missing.
    """
    # start_node and end_node can be None in some cases
    if rel.start_node is None or rel.end_node is None:
        return None

    return Edge(
        id=str(rel.element_id),
        source=str(rel.start_node.element_id),
        target=str(rel.end_node.element_id),
        data=EdgeData(
            type=rel.type,
            properties=dict(rel.items()),
        ),
    )


def _extract_graph_elements(
    results: list[dict[str, Any]],
) -> tuple[list[Node], list[Edge]]:
    """Extract nodes and edges from query results.

    Args:
        results: List of result records from Neo4j.

    Returns:
        Tuple of (nodes, edges) in Linkurious format.
    """
    nodes: dict[str, Node] = {}  # Use dict for deduplication by ID
    edges: dict[str, Edge] = {}  # Use dict for deduplication by ID

    def _process_value(value: Any) -> None:
        """Recursively process a value to extract nodes and edges."""
        if isinstance(value, Neo4jNode):
            node = _convert_neo4j_node(value)
            nodes[node.id] = node
        elif isinstance(value, Neo4jRelationship):
            edge = _convert_neo4j_relationship(value)
            if edge is not None:
                edges[edge.id] = edge
            # Also extract the start and end nodes from the relationship
            if value.start_node is not None:
                start_node = _convert_neo4j_node(value.start_node)
                nodes[start_node.id] = start_node
            if value.end_node is not None:
                end_node = _convert_neo4j_node(value.end_node)
                nodes[end_node.id] = end_node
        elif isinstance(value, list):
            for item in value:
                _process_value(item)
        elif isinstance(value, dict):
            for v in value.values():
                _process_value(v)

    for record in results:
        for value in record.values():
            _process_value(value)

    return list(nodes.values()), list(edges.values())


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        200: {"model": QueryResponse, "description": "Query executed successfully"},
        400: {"description": "Invalid query syntax"},
        403: {"description": "Write operation forbidden or authentication failed"},
        503: {"description": "Neo4j unavailable"},
        504: {"description": "Query execution timeout"},
    },
)
async def execute_query(
    request: Request,
    query_request: QueryRequest,
    database: str = Path(..., description="Target database name"),
    _: None = Depends(verify_api_key),
) -> QueryResponse | JSONResponse:
    """Execute a read-only Cypher query.

    Args:
        request: FastAPI request object.
        query_request: Query request with query string and parameters.
        database: Target database name from path.
        _: API key verification dependency.

    Returns:
        Query results in Linkurious format.
    """
    # Check if Neo4j client is available
    neo4j_client = getattr(request.app.state, "neo4j_client", None)
    if neo4j_client is None:
        logger.warning("Neo4j client not available for query execution")
        error_response = ErrorResponse(
            error=Error(
                code="NEO4J_UNAVAILABLE",
                message="Neo4j database is not available",
            )
        )
        return JSONResponse(status_code=503, content=error_response.model_dump())

    # Validate query is read-only
    if not is_read_only_query(query_request.query):
        forbidden_keyword = get_forbidden_keyword(query_request.query)
        logger.warning(
            "Write operation blocked: %s in query",
            forbidden_keyword,
        )
        error_response = ErrorResponse(
            error=Error(
                code="WRITE_OPERATION_FORBIDDEN",
                message="Write operations are not allowed. This API is read-only.",
                details={
                    "query": _truncate_query(query_request.query),
                    "forbidden_keyword": forbidden_keyword,
                    "allowed_operations": ALLOWED_OPERATIONS,
                },
            )
        )
        return JSONResponse(status_code=403, content=error_response.model_dump())

    # Execute query
    settings = get_settings()
    try:
        start_time = time.time()

        results = neo4j_client.execute_query(
            query=query_request.query,
            parameters=query_request.parameters,
            database=database,
            timeout=float(settings.query_timeout_seconds),
        )

        execution_time_ms = (time.time() - start_time) * 1000

        # Extract nodes and edges from results
        nodes, edges = _extract_graph_elements(results)

        return QueryResponse(
            nodes=nodes,
            edges=edges,
            truncatedByLimit=False,
            meta=QueryMeta(
                query_type="r",
                records_returned=len(results),
                execution_time_ms=round(execution_time_ms, 2),
            ),
        )

    except ClientError as e:
        error_msg = str(e).lower()
        # Check for timeout-related errors
        if "timeout" in error_msg or "timed out" in error_msg:
            logger.warning("Query execution timed out: %s", e)
            error_response = ErrorResponse(
                error=Error(
                    code="QUERY_TIMEOUT",
                    message="Query execution exceeded timeout limit",
                    details={
                        "timeout_seconds": settings.query_timeout_seconds,
                        "query": _truncate_query(query_request.query),
                    },
                )
            )
            return JSONResponse(status_code=504, content=error_response.model_dump())
        # Re-raise for other client errors to be handled below
        raise

    except Neo4jError as e:
        logger.error("Query execution failed: %s", e)
        error_msg = str(e)
        position = _extract_error_position(error_msg)

        details: dict[str, Any] = {
            "query": _truncate_query(query_request.query),
            "neo4j_error": error_msg,
        }
        if position is not None:
            details["position"] = position

        error_response = ErrorResponse(
            error=Error(
                code="QUERY_SYNTAX_ERROR",
                message="Invalid Cypher query syntax",
                details=details,
            )
        )
        return JSONResponse(status_code=400, content=error_response.model_dump())
