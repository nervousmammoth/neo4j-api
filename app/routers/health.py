"""Health and database listing endpoints.

Endpoints:
- GET /api/health - Health check and Neo4j connectivity
- GET /api/databases - List available Neo4j databases

This module provides public endpoints that do NOT require authentication.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models import (
    Database,
    DatabaseListResponse,
    Error,
    ErrorResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "API is healthy and Neo4j is connected",
            "model": HealthResponse,
        },
        503: {
            "description": "API is unhealthy or Neo4j is disconnected",
            "model": HealthResponse,
        },
    },
)
async def health_check(request: Request, response: Response) -> HealthResponse:
    """Health check endpoint.

    Returns API health status and Neo4j connectivity information.
    This endpoint does NOT require authentication (public endpoint).

    Args:
        request: FastAPI request object for accessing app state.
        response: FastAPI response object for setting status code.

    Returns:
        HealthResponse with status, neo4j connectivity, and version.
        Returns 200 if healthy, 503 if unhealthy.
    """
    settings = get_settings()
    version = settings.api_version

    def _unhealthy_response(error_msg: str) -> HealthResponse:
        """Create a standardized unhealthy HealthResponse."""
        response.status_code = 503
        return HealthResponse(
            status="unhealthy",
            neo4j="disconnected",
            version=version,
            error=error_msg,
        )

    # Check if Neo4j client is initialized
    neo4j_client = getattr(request.app.state, "neo4j_client", None)

    if neo4j_client is None:
        logger.warning("Health check failed: Neo4j client not initialized")
        return _unhealthy_response("Neo4j client not initialized")

    # Verify Neo4j connectivity
    try:
        connected = neo4j_client.verify_connectivity()
    except Exception as e:
        logger.error("Health check failed: Neo4j connectivity error: %s", e)
        return _unhealthy_response(str(e))

    if connected:
        logger.debug("Health check passed: Neo4j connected")
        return HealthResponse(
            status="healthy",
            neo4j="connected",
            version=version,
        )
    else:
        logger.warning("Health check failed: Neo4j connectivity returned False")
        return _unhealthy_response("Neo4j connectivity check failed")


@router.get(
    "/databases",
    response_model=DatabaseListResponse,
    responses={
        200: {
            "description": "List of available databases",
            "model": DatabaseListResponse,
        },
        500: {
            "description": "Failed to query databases",
        },
        503: {
            "description": "Neo4j client not available",
        },
    },
)
async def list_databases(request: Request) -> DatabaseListResponse | JSONResponse:
    """List all available Neo4j databases.

    Returns a list of all databases accessible in the Neo4j instance.
    This endpoint does NOT require authentication (public endpoint).

    Args:
        request: FastAPI request object for accessing app state.

    Returns:
        DatabaseListResponse with list of databases.
        Returns 200 on success, 500 on query failure, 503 if Neo4j unavailable.
    """
    # Check if Neo4j client is initialized
    neo4j_client = getattr(request.app.state, "neo4j_client", None)

    if neo4j_client is None:
        logger.warning("Database list failed: Neo4j client not initialized")
        error_response = ErrorResponse(
            error=Error(
                code="NEO4J_UNAVAILABLE",
                message="Neo4j client not initialized",
            )
        )
        return JSONResponse(status_code=503, content=error_response.model_dump())

    try:
        # Query system database for database list
        results = neo4j_client.execute_query(
            "SHOW DATABASES",
            database="system",
        )

        # Parse results into Database objects
        databases = [
            Database(
                name=record["name"],
                default=record.get("default", False),
                status=record.get("currentStatus"),
            )
            for record in results
        ]

        logger.debug("Database list retrieved: %d databases", len(databases))
        return DatabaseListResponse(databases=databases)

    except Exception as e:
        logger.error("Database list failed: %s", e)
        error_response = ErrorResponse(
            error=Error(
                code="DATABASE_QUERY_ERROR",
                message="Failed to list databases",
                details={"reason": str(e)},
            )
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())
