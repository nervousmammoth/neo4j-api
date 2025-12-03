"""
Integration tests for Neo4j database connection.

These tests require a running Neo4j instance via docker-compose.test.yml
Run: docker compose -f docker-compose.test.yml up -d --wait

Port: 7691 (unique to neo4j-api)
"""

import os

from neo4j import GraphDatabase
import pytest

# Test database configuration
TEST_URI = os.getenv("NEO4J_URI", "bolt://localhost:7691")
TEST_USER = os.getenv("NEO4J_USERNAME", "neo4j")
TEST_PASSWORD = os.getenv("NEO4J_PASSWORD", "testpassword")


@pytest.fixture(scope="module")
def driver():
    """Create a Neo4j driver for the test database."""
    drv = GraphDatabase.driver(TEST_URI, auth=(TEST_USER, TEST_PASSWORD))
    yield drv
    drv.close()


@pytest.fixture
def session(driver):
    """Create a session for each test."""
    sess = driver.session()
    yield sess
    sess.close()


@pytest.mark.integration
class TestNeo4jConnection:
    """Integration tests for Neo4j connection."""

    def test_connect_to_database(self, driver):
        """Should connect to the test database."""
        server_info = driver.get_server_info()
        assert server_info.address is not None

    def test_execute_simple_query(self, session):
        """Should execute a simple read query."""
        result = session.run("RETURN 1 as num")
        record = result.single()
        assert record["num"] == 1

    def test_transaction_rollback(self, session):
        """Should rollback transactions correctly."""
        # Start transaction and create node
        tx = session.begin_transaction()
        tx.run(
            "CREATE (n:TestNode {id: $id, name: $name}) RETURN n",
            id="test-rollback",
            name="Rollback Test Node",
        )
        # Rollback
        tx.rollback()

        # Verify node was not created
        result = session.run(
            "MATCH (n:TestNode {id: $id}) RETURN n", id="test-rollback"
        )
        assert result.single() is None

    def test_transaction_commit(self, session):
        """Should commit transactions when requested."""
        # Create and commit node
        tx = session.begin_transaction()
        tx.run(
            "CREATE (n:TestNode {id: $id, name: $name}) RETURN n",
            id="test-commit-py",
            name="Commit Test Node",
        )
        tx.commit()

        # Verify node was created
        result = session.run(
            "MATCH (n:TestNode {id: $id}) RETURN n", id="test-commit-py"
        )
        assert result.single() is not None

        # Cleanup
        session.run("MATCH (n:TestNode {id: $id}) DELETE n", id="test-commit-py")


@pytest.mark.integration
class TestReadOnlyQueries:
    """Integration tests for read-only query validation."""

    def test_match_query_succeeds(self, session):
        """Read-only MATCH query should succeed."""
        result = session.run("MATCH (n) RETURN count(n) as count")
        record = result.single()
        assert record["count"] >= 0

    def test_call_db_labels_succeeds(self, session):
        """CALL db.labels() should succeed."""
        result = session.run("CALL db.labels() YIELD label RETURN label")
        # Should not raise, labels list may be empty
        records = list(result)
        assert isinstance(records, list)

    def test_show_indexes_succeeds(self, session):
        """SHOW INDEXES should succeed."""
        result = session.run("SHOW INDEXES")
        records = list(result)
        assert isinstance(records, list)
