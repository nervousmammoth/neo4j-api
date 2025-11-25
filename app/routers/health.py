"""Health and database listing endpoints.

Endpoints:
- GET /api/health - Health check and Neo4j connectivity

This module provides public endpoints that do NOT require authentication.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models import HealthResponse

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
async def health_check(request: Request) -> HealthResponse | JSONResponse:
    """Health check endpoint.

    Returns API health status and Neo4j connectivity information.
    This endpoint does NOT require authentication (public endpoint).

    Args:
        request: FastAPI request object for accessing app state.

    Returns:
        HealthResponse with status, neo4j connectivity, and version.
        Returns 200 if healthy, 503 if unhealthy.
    """
    settings = get_settings()
    version = settings.api_version

    # Check if Neo4j client is initialized
    neo4j_client = getattr(request.app.state, "neo4j_client", None)

    if neo4j_client is None:
        logger.warning("Health check failed: Neo4j client not initialized")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "neo4j": "disconnected",
                "version": version,
                "error": "Neo4j client not initialized",
            },
        )

    # Verify Neo4j connectivity
    try:
        connected = neo4j_client.verify_connectivity()
    except Exception as e:
        logger.error("Health check failed: Neo4j connectivity error: %s", e)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "neo4j": "disconnected",
                "version": version,
                "error": str(e),
            },
        )

    if connected:
        logger.debug("Health check passed: Neo4j connected")
        return HealthResponse(
            status="healthy",
            neo4j="connected",
            version=version,
        )
    else:
        logger.warning("Health check failed: Neo4j connectivity returned False")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "neo4j": "disconnected",
                "version": version,
                "error": "Neo4j connectivity check failed",
            },
        )
