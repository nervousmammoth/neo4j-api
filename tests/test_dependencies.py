"""Unit tests for FastAPI dependency injection functions.

This module tests the API key authentication dependency.
"""

from __future__ import annotations

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from app.config import Settings  # noqa: TCH001
from app.dependencies import verify_api_key


class TestVerifyApiKey:
    """Test suite for verify_api_key dependency function."""

    @pytest.mark.asyncio
    async def test_valid_api_key_allows_access(
        self, settings_fixture: Settings
    ) -> None:
        """Test that a valid API key allows access without raising exception.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange
        valid_key = "test-api-key-12345"

        # Act & Assert - should not raise exception
        result = await verify_api_key(x_api_key=valid_key, settings=settings_fixture)
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_api_key_denies_access(
        self, settings_fixture: Settings
    ) -> None:
        """Test that an invalid API key raises 403 with structured error.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange
        invalid_key = "wrong-api-key"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key=invalid_key, settings=settings_fixture)

        # Verify status code
        assert exc_info.value.status_code == 403

        # Verify structured error response
        assert "error" in exc_info.value.detail
        error = exc_info.value.detail["error"]
        assert error["code"] == "INVALID_API_KEY"
        assert error["message"] == "Invalid API key provided"
        assert error["details"] == {}  # Empty details for consistency

    @pytest.mark.asyncio
    async def test_missing_api_key_denies_access(
        self, settings_fixture: Settings
    ) -> None:
        """Test that a missing API key (None) raises 403 with structured error.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key=None, settings=settings_fixture)

        # Verify status code
        assert exc_info.value.status_code == 403

        # Verify structured error response
        assert "error" in exc_info.value.detail
        error = exc_info.value.detail["error"]
        assert error["code"] == "MISSING_API_KEY"
        assert error["message"] == "API key is required"
        assert error["details"] == {"header": "X-API-Key"}

    @pytest.mark.asyncio
    async def test_empty_api_key_denies_access(
        self, settings_fixture: Settings
    ) -> None:
        """Test that an empty string API key raises 403 with structured error.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key="", settings=settings_fixture)

        # Verify status code
        assert exc_info.value.status_code == 403

        # Verify structured error response
        assert "error" in exc_info.value.detail
        error = exc_info.value.detail["error"]
        assert error["code"] == "MISSING_API_KEY"
        assert error["message"] == "API key is required"
        assert error["details"] == {"header": "X-API-Key"}

    @pytest.mark.asyncio
    async def test_whitespace_api_key_denies_access(
        self, settings_fixture: Settings
    ) -> None:
        """Test that a whitespace-only API key raises 403 with structured error.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key="   ", settings=settings_fixture)

        # Verify status code
        assert exc_info.value.status_code == 403

        # Verify structured error response
        assert "error" in exc_info.value.detail
        error = exc_info.value.detail["error"]
        assert error["code"] == "MISSING_API_KEY"
        assert error["message"] == "API key is required"

    @pytest.mark.asyncio
    async def test_api_key_validation_is_case_sensitive(
        self, settings_fixture: Settings
    ) -> None:
        """Test that API key comparison is case-sensitive.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange - use different case
        wrong_case_key = "TEST-API-KEY-12345"  # Should be lowercase 'test'

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key=wrong_case_key, settings=settings_fixture)

        # Verify 403 status
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"]["code"] == "INVALID_API_KEY"

    @pytest.mark.asyncio
    async def test_api_key_with_extra_whitespace_fails(
        self, settings_fixture: Settings
    ) -> None:
        """Test that API key with leading/trailing whitespace is treated as invalid.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange - valid key but with whitespace
        key_with_whitespace = "  test-api-key-12345  "

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(
                x_api_key=key_with_whitespace, settings=settings_fixture
            )

        # Verify 403 status (whitespace makes it different from configured key)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"]["code"] == "INVALID_API_KEY"


class TestVerifyApiKeyIntegration:
    """Integration tests for verify_api_key with FastAPI TestClient."""

    def test_protected_endpoint_with_valid_api_key(
        self, settings_fixture: Settings
    ) -> None:
        """Test that a protected endpoint allows access with valid API key.

        This integration test verifies the dependency works correctly when
        used in a FastAPI route.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange - create a minimal FastAPI app for testing
        from fastapi import Depends, FastAPI

        app = FastAPI()

        # Override settings dependency
        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        @app.get("/protected")
        async def protected_route(
            _: None = Depends(verify_api_key),
        ) -> dict[str, str]:
            return {"message": "Access granted"}

        client = TestClient(app)

        # Act
        response = client.get("/protected", headers={"X-API-Key": "test-api-key-12345"})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": "Access granted"}

    def test_protected_endpoint_without_api_key(
        self, settings_fixture: Settings
    ) -> None:
        """Test that a protected endpoint denies access without API key.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange
        from fastapi import Depends, FastAPI

        app = FastAPI()

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        @app.get("/protected")
        async def protected_route(
            _: None = Depends(verify_api_key),
        ) -> dict[str, str]:
            return {"message": "Access granted"}

        client = TestClient(app)

        # Act
        response = client.get("/protected")

        # Assert
        assert response.status_code == 403
        error_data = response.json()
        assert "detail" in error_data
        assert error_data["detail"]["error"]["code"] == "MISSING_API_KEY"

    def test_protected_endpoint_with_invalid_api_key(
        self, settings_fixture: Settings
    ) -> None:
        """Test that a protected endpoint denies access with invalid API key.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange
        from fastapi import Depends, FastAPI

        app = FastAPI()

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        @app.get("/protected")
        async def protected_route(
            _: None = Depends(verify_api_key),
        ) -> dict[str, str]:
            return {"message": "Access granted"}

        client = TestClient(app)

        # Act
        response = client.get("/protected", headers={"X-API-Key": "wrong-key"})

        # Assert
        assert response.status_code == 403
        error_data = response.json()
        assert "detail" in error_data
        assert error_data["detail"]["error"]["code"] == "INVALID_API_KEY"

    def test_header_name_is_case_insensitive(self, settings_fixture: Settings) -> None:
        """Test that the X-API-Key header name is case-insensitive.

        FastAPI's Header() automatically handles case-insensitive header lookup.

        Args:
            settings_fixture: Test settings with configured API key.
        """
        # Arrange
        from fastapi import Depends, FastAPI

        app = FastAPI()

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        @app.get("/protected")
        async def protected_route(
            _: None = Depends(verify_api_key),
        ) -> dict[str, str]:
            return {"message": "Access granted"}

        client = TestClient(app)

        # Act - test different header name cases
        response1 = client.get(
            "/protected", headers={"X-API-Key": "test-api-key-12345"}
        )
        response2 = client.get(
            "/protected", headers={"x-api-key": "test-api-key-12345"}
        )
        response3 = client.get(
            "/protected", headers={"X-Api-Key": "test-api-key-12345"}
        )

        # Assert - all should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
