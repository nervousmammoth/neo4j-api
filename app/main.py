"""FastAPI application entry point.

This module contains the FastAPI application instance, lifespan management,
and router registration.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI

from app.config import get_settings
from app.utils.neo4j_client import Neo4jClient

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

# Global Neo4j client instance
neo4j_client: Neo4jClient | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan.

    Startup:
        - Create Neo4j client
        - Verify database connectivity

    Shutdown:
        - Close Neo4j client

    Args:
        _app: FastAPI application instance (unused, required by signature).

    Yields:
        None
    """
    global neo4j_client

    # Startup
    settings = get_settings()
    logger.info("Starting Neo4j API application")

    try:
        neo4j_client = Neo4jClient(settings)
        if neo4j_client.verify_connectivity():
            logger.info("Neo4j connectivity verified")
        else:
            logger.warning("Neo4j connectivity check failed")
    except Exception as e:
        logger.error("Failed to initialize Neo4j client: %s", e)
        neo4j_client = None

    yield

    # Shutdown
    logger.info("Shutting down Neo4j API application")
    if neo4j_client:
        neo4j_client.close()
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


def get_neo4j_client() -> Neo4jClient:
    """Get Neo4j client instance.

    Returns:
        Neo4j client instance.

    Raises:
        RuntimeError: If Neo4j client not initialized.
    """
    if neo4j_client is None:
        raise RuntimeError("Neo4j client not initialized")
    return neo4j_client


# Routers will be added in subsequent issues:
# app.include_router(health.router)
# app.include_router(search.router)
# etc.
