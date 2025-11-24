"""Tests for FastAPI application entry point.

This module tests the FastAPI application instance, lifespan management,
and Neo4j client dependency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
import pytest

if TYPE_CHECKING:
    from app.config import Settings


@pytest.fixture
def mock_neo4j_client_class() -> MagicMock:
    """Provide a mock Neo4jClient class.

    Returns:
        Mock Neo4jClient class with verify_connectivity() and close() methods.
    """
    mock_client = MagicMock()
    mock_client.verify_connectivity.return_value = True
    mock_client.close.return_value = None
    return mock_client


def test_app_instance_exists(settings_fixture: Settings) -> None:
    """Test that FastAPI app instance is created.

    Args:
        settings_fixture: Test settings fixture.
    """
    from app.main import app

    assert isinstance(app, FastAPI)


def test_app_configuration(settings_fixture: Settings) -> None:
    """Test that app is configured with correct metadata.

    Args:
        settings_fixture: Test settings fixture.
    """
    from app.main import app

    assert app.title == settings_fixture.api_title
    assert app.version == settings_fixture.api_version


def test_app_openapi_urls(settings_fixture: Settings) -> None:
    """Test that OpenAPI documentation URLs are configured correctly.

    Args:
        settings_fixture: Test settings fixture.
    """
    from app.main import app

    expected_prefix = settings_fixture.api_prefix
    assert app.docs_url == f"{expected_prefix}/docs"
    assert app.redoc_url == f"{expected_prefix}/redoc"
    assert app.openapi_url == f"{expected_prefix}/openapi.json"


@pytest.mark.asyncio
async def test_lifespan_creates_neo4j_client(
    settings_fixture: Settings,
    mock_neo4j_client_class: MagicMock,
) -> None:
    """Test that lifespan startup creates Neo4j client.

    Args:
        settings_fixture: Test settings fixture.
        mock_neo4j_client_class: Mock Neo4jClient class.
    """
    with patch("app.main.Neo4jClient", return_value=mock_neo4j_client_class):
        from app.main import lifespan

        # Create a test app for lifespan
        test_app = FastAPI()

        async with lifespan(test_app):
            # During lifespan, client should be created and connectivity verified
            assert hasattr(test_app.state, "neo4j_client")
            assert test_app.state.neo4j_client is mock_neo4j_client_class

        # Verify Neo4jClient was instantiated
        # Verify connectivity was checked
        mock_neo4j_client_class.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_closes_neo4j_client(
    settings_fixture: Settings,
    mock_neo4j_client_class: MagicMock,
) -> None:
    """Test that lifespan shutdown closes Neo4j client.

    Args:
        settings_fixture: Test settings fixture.
        mock_neo4j_client_class: Mock Neo4jClient class.
    """
    with patch("app.main.Neo4jClient", return_value=mock_neo4j_client_class):
        from app.main import lifespan

        test_app = FastAPI()

        async with lifespan(test_app):
            # Client should be set during lifespan
            assert test_app.state.neo4j_client is mock_neo4j_client_class

        # After lifespan exits, client should be closed
        mock_neo4j_client_class.close.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_handles_connectivity_check_exception(
    settings_fixture: Settings,
) -> None:
    """Test that lifespan handles exceptions during connectivity check.

    Args:
        settings_fixture: Test settings fixture.
    """
    mock_client = MagicMock()
    mock_client.verify_connectivity.side_effect = Exception("Connection failed")

    with patch("app.main.Neo4jClient", return_value=mock_client):
        from app.main import lifespan

        test_app = FastAPI()

        # Should not raise, just log error
        async with lifespan(test_app):
            # Client should be set to None after exception
            assert hasattr(test_app.state, "neo4j_client")
            assert test_app.state.neo4j_client is None

        # Client creation was attempted
        mock_client.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_handles_client_creation_error(
    settings_fixture: Settings,
) -> None:
    """Test that lifespan handles exceptions during Neo4j client creation.

    Args:
        settings_fixture: Test settings fixture.
    """
    with patch("app.main.Neo4jClient", side_effect=Exception("Invalid configuration")):
        from app.main import lifespan

        test_app = FastAPI()

        # Should not raise, just log error
        async with lifespan(test_app):
            # Client should be set to None after creation error
            assert hasattr(test_app.state, "neo4j_client")
            assert test_app.state.neo4j_client is None


@pytest.mark.asyncio
async def test_lifespan_handles_neo4j_connectivity_failure(
    settings_fixture: Settings,
) -> None:
    """Test that lifespan handles Neo4j connectivity check failure.

    Args:
        settings_fixture: Test settings fixture.
    """
    mock_client = MagicMock()
    mock_client.verify_connectivity.return_value = False

    with patch("app.main.Neo4jClient", return_value=mock_client):
        from app.main import lifespan

        test_app = FastAPI()

        # Should not raise, just log warning
        async with lifespan(test_app):
            # Client should be set to None after connectivity failure
            assert hasattr(test_app.state, "neo4j_client")
            assert test_app.state.neo4j_client is None

        # Connectivity check was attempted
        mock_client.verify_connectivity.assert_called_once()
        # Client should be closed immediately when verification fails
        mock_client.close.assert_called_once()


def test_get_neo4j_client_returns_client(
    settings_fixture: Settings,
    mock_neo4j_client_class: MagicMock,
) -> None:
    """Test that get_neo4j_client returns the initialized client.

    Args:
        settings_fixture: Test settings fixture.
        mock_neo4j_client_class: Mock Neo4jClient class.
    """
    from app.main import app, get_neo4j_client

    # Set client in app state
    app.state.neo4j_client = mock_neo4j_client_class

    # Create mock request
    mock_request = MagicMock()
    mock_request.app = app

    client = get_neo4j_client(mock_request)
    assert client is mock_neo4j_client_class


def test_get_neo4j_client_raises_when_not_initialized(
    settings_fixture: Settings,
) -> None:
    """Test that get_neo4j_client raises RuntimeError when client not initialized.

    Args:
        settings_fixture: Test settings fixture.
    """
    from app.main import app, get_neo4j_client

    # Set client to None in app state
    app.state.neo4j_client = None

    # Create mock request
    mock_request = MagicMock()
    mock_request.app = app

    with pytest.raises(RuntimeError, match="Neo4j client not initialized"):
        get_neo4j_client(mock_request)


def test_app_has_lifespan_configured(settings_fixture: Settings) -> None:
    """Test that app has lifespan context manager configured.

    Args:
        settings_fixture: Test settings fixture.
    """
    from app.main import app

    # FastAPI stores lifespan in router.lifespan_context
    assert app.router.lifespan_context is not None
