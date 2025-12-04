"""Unit tests for health check endpoint.

This module tests the GET /api/health endpoint following TDD principles.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings  # noqa: TCH001
from app.models import HealthResponse


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

    def test_unhealthy_response_conforms_to_health_response_model(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Verify 503 response conforms to HealthResponse model and contains all fields.

        This ensures the OpenAPI documentation contract is honored and that clients
        using code generation will get correct type definitions.

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

        # Assert - Response validates against HealthResponse model
        assert response.status_code == 503
        data = response.json()

        # This should NOT raise ValidationError
        try:
            validated = HealthResponse(**data)
        except ValidationError as e:
            raise AssertionError(
                f"503 response does not validate against HealthResponse model: {e}"
            ) from e

        # Assert field values on the validated model
        assert validated.status == "unhealthy"
        assert validated.neo4j == "disconnected"
        assert validated.version == settings_fixture.api_version
        assert isinstance(validated.error, str)


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


class TestDatabasesListSuccess:
    """Test successful databases list scenarios."""

    def test_databases_returns_200_on_success(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test databases list returns 200 when query succeeds.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"name": "neo4j", "default": True, "currentStatus": "online"},
            {"name": "system", "default": False, "currentStatus": "online"},
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 200

    def test_databases_response_format_matches_spec(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that databases response format matches specification.

        Response must include: databases array with name, default, status fields.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"name": "neo4j", "default": True, "currentStatus": "online"},
            {"name": "investigation_001", "default": False, "currentStatus": "online"},
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify databases array exists
        assert "databases" in data
        assert isinstance(data["databases"], list)

        # Verify each database has required fields
        for db in data["databases"]:
            assert "name" in db
            assert "default" in db
            assert isinstance(db["name"], str)
            assert isinstance(db["default"], bool)

    def test_databases_no_auth_required(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that databases endpoint does NOT require authentication.

        The /api/databases endpoint must be public - no X-API-Key header needed.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"name": "neo4j", "default": True, "currentStatus": "online"},
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act - Make request WITHOUT X-API-Key header
        response = client.get("/api/databases")

        # Assert - Should succeed without authentication
        assert response.status_code == 200
        assert response.status_code != 401
        assert response.status_code != 403

    def test_databases_returns_list_of_databases(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that databases endpoint returns correct list of databases.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"name": "neo4j", "default": True, "currentStatus": "online"},
            {"name": "system", "default": False, "currentStatus": "online"},
            {"name": "investigation_001", "default": False, "currentStatus": "online"},
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["databases"]) == 3

        # Check database names
        db_names = [db["name"] for db in data["databases"]]
        assert "neo4j" in db_names
        assert "system" in db_names
        assert "investigation_001" in db_names

    def test_databases_default_database_marked_correctly(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that the default database is marked correctly.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"name": "neo4j", "default": True, "currentStatus": "online"},
            {"name": "system", "default": False, "currentStatus": "online"},
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Find neo4j database and verify it's marked as default
        neo4j_db = next(db for db in data["databases"] if db["name"] == "neo4j")
        assert neo4j_db["default"] is True

        # Find system database and verify it's not default
        system_db = next(db for db in data["databases"] if db["name"] == "system")
        assert system_db["default"] is False

    def test_databases_includes_status_field(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that databases response includes status field.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"name": "neo4j", "default": True, "currentStatus": "online"},
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["databases"][0]["status"] == "online"


class TestDatabasesListFailure:
    """Test databases list failure scenarios."""

    def test_databases_returns_500_on_query_failure(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test databases returns 500 when query execution fails.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.side_effect = Exception("Permission denied")
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "DATABASE_QUERY_ERROR"
        assert data["error"]["message"] == "Failed to list databases"
        assert data["error"]["details"] == {"reason": "Permission denied"}

    def test_databases_returns_503_when_neo4j_unavailable(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test databases returns 503 when Neo4j client is not available.

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
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NEO4J_UNAVAILABLE"
        assert data["error"]["details"] == {}


class TestDatabasesListEdgeCases:
    """Test databases list edge cases."""

    def test_databases_handles_empty_database_list(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test databases handles empty database list.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "databases" in data
        assert data["databases"] == []

    def test_databases_handles_missing_optional_fields(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test databases handles missing optional fields in Neo4j response.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.health import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        # Neo4j response might not have all fields
        mock_client.execute_query.return_value = [
            {"name": "neo4j", "default": True},  # Missing currentStatus
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get("/api/databases")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["databases"][0]["name"] == "neo4j"
        assert data["databases"][0]["default"] is True
        # Status should be None or missing when not provided
        assert data["databases"][0].get("status") is None
