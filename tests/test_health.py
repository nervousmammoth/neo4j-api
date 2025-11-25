"""Unit tests for health check endpoint.

This module tests the GET /api/health endpoint following TDD principles.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings  # noqa: TCH001


class TestHealthCheckSuccess:
    """Test successful health check scenarios."""

    def test_health_check_returns_200_when_neo4j_connected(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test health check returns 200 when Neo4j is connected.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange - create FastAPI app with health router
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        # Create mock Neo4j client
        mock_client = MagicMock()
        mock_client.verify_connectivity.return_value = True

        # Store in app state (simulating lifespan behavior)
        app.state.neo4j_client = mock_client

        # Override settings
        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["neo4j"] == "connected"

    def test_health_check_response_format_matches_spec(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that health check response format matches specification.

        Response must include: status, neo4j, version fields.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.verify_connectivity.return_value = True
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        assert "status" in data
        assert "neo4j" in data
        assert "version" in data

        # Verify field values match spec
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["neo4j"] in ["connected", "disconnected"]
        assert isinstance(data["version"], str)
        assert data["version"] == settings_fixture.api_version

    def test_health_check_no_auth_required(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that health check endpoint does NOT require authentication.

        The /api/health endpoint must be public - no X-API-Key header needed.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.verify_connectivity.return_value = True
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act - Make request WITHOUT X-API-Key header
        response = client.get("/api/health")

        # Assert - Should succeed without authentication
        assert response.status_code == 200
        # Verify it's not a 401 or 403 authentication error
        assert response.status_code != 401
        assert response.status_code != 403


class TestHealthCheckFailure:
    """Test health check failure scenarios."""

    def test_health_check_returns_503_when_neo4j_disconnected(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test health check returns 503 when Neo4j connectivity fails.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.verify_connectivity.return_value = False
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["neo4j"] == "disconnected"

    def test_health_check_returns_error_message_on_failure(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that health check includes error message when unhealthy.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.verify_connectivity.return_value = False
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert isinstance(data["error"], str)


class TestHealthCheckEdgeCases:
    """Test health check edge cases."""

    def test_health_check_handles_neo4j_client_not_initialized(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test health check returns 503 when Neo4j client is None.

        This can happen if Neo4j connection failed during app startup.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        # Set client to None (simulating failed initialization)
        app.state.neo4j_client = None

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/health")

        # Assert - Should return 503, not crash
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["neo4j"] == "disconnected"
        assert "error" in data

    def test_health_check_handles_verify_connectivity_exception(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test health check handles exceptions from verify_connectivity.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.verify_connectivity.side_effect = Exception(
            "Connection refused to bolt://localhost:7687"
        )
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/health")

        # Assert - Should return 503 with error message
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["neo4j"] == "disconnected"
        assert "error" in data
        assert "Connection refused" in data["error"]
