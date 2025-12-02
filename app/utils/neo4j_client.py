"""Neo4j database client wrapper.

This module provides a wrapper around the Neo4j Python driver with
multi-database support and connection pooling.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j database client with multi-database support.

    This class wraps the Neo4j Python driver and provides a clean interface
    for executing queries across multiple databases.

    Attributes:
        driver: Neo4j driver instance.
        settings: Application settings.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize Neo4j client with settings.

        Args:
            settings: Application settings containing Neo4j configuration.

        Raises:
            ServiceUnavailable: If connection cannot be established.
        """
        self.settings = settings
        self.driver: Driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password.get_secret_value()),
            max_connection_lifetime=settings.neo4j_max_connection_lifetime,
            max_connection_pool_size=settings.neo4j_max_connection_pool_size,
            connection_timeout=settings.neo4j_connection_timeout,
        )
        logger.info("Neo4j driver initialized for %s", settings.neo4j_uri)

    def verify_connectivity(self) -> bool:
        """Verify Neo4j database connectivity.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            self.driver.verify_connectivity()
            logger.info("Neo4j connectivity verified")
            return True
        except ServiceUnavailable as e:
            logger.error("Neo4j service unavailable: %s", e)
            return False
        except Neo4jError as e:
            logger.error("Neo4j connectivity error: %s", e)
            return False

    def execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        database: str | None = None,
        timeout: float | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query.

        Args:
            query: Cypher query string.
            parameters: Query parameters (optional).
            database: Database name (optional, uses default if not specified).
            timeout: Query timeout in seconds (optional).

        Returns:
            List of result records as dictionaries.

        Raises:
            Neo4jError: If query execution fails.
        """
        db = database or self.settings.neo4j_database
        params = parameters or {}

        try:
            with self.driver.session(database=db) as session:
                result = session.run(query, params, timeout=timeout)
                records = [record.data() for record in result]
                logger.debug(
                    "Executed query on database '%s', returned %d records",
                    db,
                    len(records),
                )
                return records
        except Neo4jError as e:
            logger.error("Query execution error on database '%s': %s", db, e)
            raise

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed")

    def __enter__(self) -> Neo4jClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.close()
