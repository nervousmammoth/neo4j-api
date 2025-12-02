"""Unit tests for Neo4j client wrapper.

This module tests the Neo4jClient class that wraps the Neo4j Python driver.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from neo4j.exceptions import Neo4jError, ServiceUnavailable
import pytest

from app.utils.neo4j_client import Neo4jClient

if TYPE_CHECKING:
    from app.config import Settings


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_client_init_creates_driver_with_correct_params(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test that Neo4jClient initializes driver with correct parameters.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver

    client = Neo4jClient(settings_fixture)

    # Verify driver was created with correct parameters
    mock_graph_database.assert_called_once_with(
        settings_fixture.neo4j_uri,
        auth=(
            settings_fixture.neo4j_username,
            settings_fixture.neo4j_password.get_secret_value(),
        ),
        max_connection_lifetime=settings_fixture.neo4j_max_connection_lifetime,
        max_connection_pool_size=settings_fixture.neo4j_max_connection_pool_size,
        connection_timeout=settings_fixture.neo4j_connection_timeout,
    )
    assert client.driver == mock_neo4j_driver
    assert client.settings == settings_fixture


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_verify_connectivity_returns_true_on_success(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test verify_connectivity returns True when connection succeeds.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.verify_connectivity.return_value = None

    client = Neo4jClient(settings_fixture)
    result = client.verify_connectivity()

    assert result is True
    mock_neo4j_driver.verify_connectivity.assert_called_once()


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_verify_connectivity_returns_false_on_service_unavailable(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test verify_connectivity returns False when Neo4j is unavailable.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.verify_connectivity.side_effect = ServiceUnavailable(
        "Connection refused"
    )

    client = Neo4jClient(settings_fixture)
    result = client.verify_connectivity()

    assert result is False
    mock_neo4j_driver.verify_connectivity.assert_called_once()


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_verify_connectivity_returns_false_on_neo4j_error(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test verify_connectivity returns False on general Neo4j errors.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.verify_connectivity.side_effect = Neo4jError("Auth failed")

    client = Neo4jClient(settings_fixture)
    result = client.verify_connectivity()

    assert result is False
    mock_neo4j_driver.verify_connectivity.assert_called_once()


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_execute_query_basic(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    mock_neo4j_session: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test execute_query executes a basic query successfully.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        mock_neo4j_session: Mock session fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.session.return_value = mock_neo4j_session

    # Create mock records
    mock_record1 = MagicMock()
    mock_record1.data.return_value = {"name": "Alice", "age": 30}
    mock_record2 = MagicMock()
    mock_record2.data.return_value = {"name": "Bob", "age": 25}
    mock_neo4j_session.run.return_value = [mock_record1, mock_record2]

    client = Neo4jClient(settings_fixture)
    query = "MATCH (n:Person) RETURN n.name AS name, n.age AS age"
    result = client.execute_query(query)

    # Verify session was created with default database
    mock_neo4j_driver.session.assert_called_once_with(
        database=settings_fixture.neo4j_database
    )

    # Verify query was executed
    mock_neo4j_session.run.assert_called_once_with(query, {}, timeout=None)

    # Verify results
    assert len(result) == 2
    assert result[0] == {"name": "Alice", "age": 30}
    assert result[1] == {"name": "Bob", "age": 25}


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_execute_query_with_parameters(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    mock_neo4j_session: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test execute_query with query parameters.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        mock_neo4j_session: Mock session fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.session.return_value = mock_neo4j_session

    mock_record = MagicMock()
    mock_record.data.return_value = {"name": "Alice"}
    mock_neo4j_session.run.return_value = [mock_record]

    client = Neo4jClient(settings_fixture)
    query = "MATCH (n:Person {name: $name}) RETURN n.name AS name"
    parameters = {"name": "Alice"}
    result = client.execute_query(query, parameters=parameters)

    # Verify query was executed with parameters
    mock_neo4j_session.run.assert_called_once_with(query, parameters, timeout=None)
    assert len(result) == 1
    assert result[0] == {"name": "Alice"}


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_execute_query_with_specific_database(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    mock_neo4j_session: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test execute_query with specific database routing.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        mock_neo4j_session: Mock session fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.session.return_value = mock_neo4j_session

    mock_record = MagicMock()
    mock_record.data.return_value = {"count": 42}
    mock_neo4j_session.run.return_value = [mock_record]

    client = Neo4jClient(settings_fixture)
    query = "MATCH (n) RETURN count(n) AS count"
    result = client.execute_query(query, database="investigation_001")

    # Verify session was created with specific database
    mock_neo4j_driver.session.assert_called_once_with(database="investigation_001")
    assert len(result) == 1
    assert result[0] == {"count": 42}


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_execute_query_uses_default_database(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    mock_neo4j_session: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test execute_query uses default database when not specified.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        mock_neo4j_session: Mock session fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.session.return_value = mock_neo4j_session

    mock_record = MagicMock()
    mock_record.data.return_value = {"result": "ok"}
    mock_neo4j_session.run.return_value = [mock_record]

    client = Neo4jClient(settings_fixture)
    query = "RETURN 'ok' AS result"
    client.execute_query(query)

    # Verify session was created with default database from settings
    mock_neo4j_driver.session.assert_called_once_with(
        database=settings_fixture.neo4j_database
    )


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_execute_query_raises_neo4j_error(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    mock_neo4j_session: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test execute_query raises Neo4jError on query failure.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        mock_neo4j_session: Mock session fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver
    mock_neo4j_driver.session.return_value = mock_neo4j_session
    mock_neo4j_session.run.side_effect = Neo4jError("Query syntax error")

    client = Neo4jClient(settings_fixture)
    query = "INVALID QUERY"

    with pytest.raises(Neo4jError, match="Query syntax error"):
        client.execute_query(query)


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_close_calls_driver_close(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test close() calls driver.close().

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver

    client = Neo4jClient(settings_fixture)
    client.close()

    mock_neo4j_driver.close.assert_called_once()


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_context_manager_calls_close_on_exit(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test context manager calls close() on exit.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver

    with Neo4jClient(settings_fixture) as client:
        assert isinstance(client, Neo4jClient)

    # Verify driver was closed when exiting context
    mock_neo4j_driver.close.assert_called_once()


@patch("app.utils.neo4j_client.GraphDatabase.driver")
def test_close_handles_none_driver(
    mock_graph_database: MagicMock,
    mock_neo4j_driver: MagicMock,
    settings_fixture: Settings,
) -> None:
    """Test close() handles case where driver is None.

    Args:
        mock_graph_database: Mock GraphDatabase.driver.
        mock_neo4j_driver: Mock driver fixture.
        settings_fixture: Test settings fixture.
    """
    mock_graph_database.return_value = mock_neo4j_driver

    client = Neo4jClient(settings_fixture)
    # Manually set driver to None to test edge case
    client.driver = None  # type: ignore[assignment]
    # Should not raise an exception
    client.close()

    # Verify close was not called (since driver was None)
    mock_neo4j_driver.close.assert_not_called()
