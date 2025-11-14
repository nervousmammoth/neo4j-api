"""Pytest configuration and shared fixtures.

This module provides reusable fixtures for testing the Neo4j API.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.config import Settings


@pytest.fixture
def settings_fixture(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Provide a test Settings instance with valid configuration.

    Args:
        monkeypatch: Pytest monkeypatch fixture for environment manipulation.

    Returns:
        Settings instance configured for testing.
    """
    # Set test environment variables
    monkeypatch.setenv("API_KEY", "test-api-key-12345")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "test-password")
    monkeypatch.setenv("NEO4J_DATABASE", "neo4j")

    # Clear settings cache and create new instance
    Settings.model_config["_env_file"] = None
    return Settings()


@pytest.fixture
def mock_neo4j_result() -> MagicMock:
    """Provide a mock Neo4j query result.

    Returns:
        Mock result object with data() method.
    """
    mock_result = MagicMock()
    mock_result.data.return_value = {"name": "test", "value": 123}
    return mock_result


@pytest.fixture
def mock_neo4j_session(mock_neo4j_result: MagicMock) -> MagicMock:
    """Provide a mock Neo4j session.

    Args:
        mock_neo4j_result: Mock result fixture.

    Returns:
        Mock session object with run() method and context manager support.
    """
    mock_session = MagicMock()
    mock_session.run.return_value = [mock_neo4j_result]
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    return mock_session


@pytest.fixture
def mock_neo4j_driver(mock_neo4j_session: MagicMock) -> MagicMock:
    """Provide a mock Neo4j driver.

    Args:
        mock_neo4j_session: Mock session fixture.

    Returns:
        Mock driver object with verify_connectivity(), session(), and close() methods.
    """
    mock_driver = MagicMock()
    mock_driver.verify_connectivity.return_value = None
    mock_driver.session.return_value = mock_neo4j_session
    mock_driver.close.return_value = None
    return mock_driver
