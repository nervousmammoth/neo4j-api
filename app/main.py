"""FastAPI application entry point.

This module contains the FastAPI application instance, lifespan management,
and router registration.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import TYPE_CHECKING, cast

from fastapi import FastAPI, Request

from app.config import get_settings
from app.routers import health
from app.utils.neo4j_client import Neo4jClient

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan.

    Startup:
        - Create Neo4j client
        - Verify database connectivity

    Shutdown:
        - Close Neo4j client

    Args:
        app: FastAPI application instance.

    Yields:
        None
    """
    # Startup
    settings = get_settings()
    logger.info("Starting Neo4j API application")

    try:
        client = Neo4jClient(settings)
        if client.verify_connectivity():
            logger.info("Neo4j connectivity verified")
            app.state.neo4j_client = client
        else:
            logger.warning("Neo4j connectivity check failed")
            client.close()
            app.state.neo4j_client = None
    except Exception as e:
        logger.error("Failed to initialize Neo4j client: %s", e)
        app.state.neo4j_client = None

    yield

    # Shutdown
    logger.info("Shutting down Neo4j API application")
    if hasattr(app.state, "neo4j_client") and app.state.neo4j_client:
        app.state.neo4j_client.close()
        logger.info("Neo4j client closed")


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)


def get_neo4j_client(request: Request) -> Neo4jClient:
    """Get Neo4j client instance.

    Args:
        request: FastAPI request object.

    Returns:
        Neo4j client instance.

    Raises:
        RuntimeError: If Neo4j client not initialized.
    """
    if (
        not hasattr(request.app.state, "neo4j_client")
        or request.app.state.neo4j_client is None
    ):
        raise RuntimeError("Neo4j client not initialized")
    return cast(Neo4jClient, request.app.state.neo4j_client)


# Register routers
app.include_router(health.router)

# Additional routers will be added in subsequent issues:
# app.include_router(search.router)
# etc.
