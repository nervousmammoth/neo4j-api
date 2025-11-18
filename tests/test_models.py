"""Unit tests for Pydantic models.

Tests follow TDD principles and ensure 100% coverage for app.models.
"""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from app.models import Error, ErrorResponse, SuccessResponse


class TestErrorModel:
    """Test cases for the Error model."""

    def test_error_creation_with_required_fields(self) -> None:
        """Test creating Error with only required fields (code and message)."""
        error = Error(code="NODE_NOT_FOUND", message="Node with ID '12345' not found")

        assert error.code == "NODE_NOT_FOUND"
        assert error.message == "Node with ID '12345' not found"
        assert error.details is None

    def test_error_creation_with_details(self) -> None:
        """Test creating Error with optional details field."""
        error = Error(
            code="VALIDATION_ERROR",
            message="Query validation failed",
            details={"forbidden_keyword": "CREATE", "line": 1},
        )

        assert error.code == "VALIDATION_ERROR"
        assert error.message == "Query validation failed"
        assert error.details == {"forbidden_keyword": "CREATE", "line": 1}

    def test_error_serialization_without_details(self) -> None:
        """Test Error serialization to dict without details."""
        error = Error(code="AUTH_FAILED", message="Invalid API key")

        result = error.model_dump()

        assert result == {
            "code": "AUTH_FAILED",
            "message": "Invalid API key",
            "details": None,
        }

    def test_error_serialization_with_details(self) -> None:
        """Test Error serialization to dict with details."""
        error = Error(
            code="DATABASE_ERROR",
            message="Connection failed",
            details={"database": "neo4j", "timeout": 5000},
        )

        result = error.model_dump()

        assert result == {
            "code": "DATABASE_ERROR",
            "message": "Connection failed",
            "details": {"database": "neo4j", "timeout": 5000},
        }

    def test_error_serialization_exclude_none(self) -> None:
        """Test Error serialization excluding None values."""
        error = Error(code="TEST_ERROR", message="Test message")

        result = error.model_dump(exclude_none=True)

        assert result == {"code": "TEST_ERROR", "message": "Test message"}
        assert "details" not in result

    def test_error_field_validation_missing_code(self) -> None:
        """Test that Error requires code field."""
        with pytest.raises(ValidationError) as exc_info:
            Error(message="Missing code field")

        assert "code" in str(exc_info.value)

    def test_error_field_validation_missing_message(self) -> None:
        """Test that Error requires message field."""
        with pytest.raises(ValidationError) as exc_info:
            Error(code="TEST_CODE")

        assert "message" in str(exc_info.value)

    def test_error_details_accepts_any_dict(self) -> None:
        """Test that details field accepts various dict structures."""
        # Nested dict
        error1 = Error(
            code="COMPLEX_ERROR",
            message="Complex details",
            details={"nested": {"key": "value"}, "list": [1, 2, 3]},
        )
        assert error1.details["nested"]["key"] == "value"

        # Empty dict
        error2 = Error(code="EMPTY_DETAILS", message="Empty", details={})
        assert error2.details == {}


class TestErrorResponseModel:
    """Test cases for the ErrorResponse model."""

    def test_error_response_creation(self) -> None:
        """Test creating ErrorResponse with nested Error object."""
        error = Error(code="NOT_FOUND", message="Resource not found")
        response = ErrorResponse(error=error)

        assert response.error.code == "NOT_FOUND"
        assert response.error.message == "Resource not found"
        assert response.error.details is None

    def test_error_response_creation_with_details(self) -> None:
        """Test creating ErrorResponse with Error containing details."""
        error = Error(
            code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "query", "reason": "Contains forbidden keyword"},
        )
        response = ErrorResponse(error=error)

        assert response.error.code == "VALIDATION_ERROR"
        assert response.error.details["field"] == "query"

    def test_error_response_serialization(self) -> None:
        """Test ErrorResponse serialization to nested dict structure."""
        error = Error(
            code="NODE_NOT_FOUND",
            message="Node with ID '12345' not found",
            details={"node_id": "12345", "database": "neo4j"},
        )
        response = ErrorResponse(error=error)

        result = response.model_dump()

        assert result == {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Node with ID '12345' not found",
                "details": {"node_id": "12345", "database": "neo4j"},
            }
        }

    def test_error_response_serialization_without_details(self) -> None:
        """Test ErrorResponse serialization when Error has no details."""
        error = Error(code="AUTH_REQUIRED", message="Authentication required")
        response = ErrorResponse(error=error)

        result = response.model_dump()

        assert result == {
            "error": {
                "code": "AUTH_REQUIRED",
                "message": "Authentication required",
                "details": None,
            }
        }

    def test_error_response_serialization_exclude_none(self) -> None:
        """Test ErrorResponse serialization excluding None values."""
        error = Error(code="SIMPLE_ERROR", message="Simple error message")
        response = ErrorResponse(error=error)

        result = response.model_dump(exclude_none=True)

        assert result == {
            "error": {"code": "SIMPLE_ERROR", "message": "Simple error message"}
        }
        assert "details" not in result["error"]

    def test_error_response_json_structure_matches_spec(self) -> None:
        """Test that JSON structure matches Linkurious API specification."""
        error = Error(
            code="WRITE_OPERATION_FORBIDDEN",
            message="Write operations are not allowed",
            details={"forbidden_keyword": "CREATE", "query": "CREATE (n) RETURN n"},
        )
        response = ErrorResponse(error=error)

        json_dict = response.model_dump()

        # Verify nested structure as per spec
        assert "error" in json_dict
        assert "code" in json_dict["error"]
        assert "message" in json_dict["error"]
        assert "details" in json_dict["error"]
        assert json_dict["error"]["code"] == "WRITE_OPERATION_FORBIDDEN"

    def test_error_response_from_dict(self) -> None:
        """Test creating ErrorResponse from dictionary (deserialization)."""
        data = {
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Connection timeout",
                "details": {"timeout_ms": 5000},
            }
        }

        response = ErrorResponse(**data)

        assert response.error.code == "DATABASE_ERROR"
        assert response.error.message == "Connection timeout"
        assert response.error.details["timeout_ms"] == 5000

    def test_error_response_validation_requires_error(self) -> None:
        """Test that ErrorResponse requires error field."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse()

        assert "error" in str(exc_info.value)


class TestSuccessResponseModel:
    """Test cases for the SuccessResponse model."""

    def test_success_response_with_defaults(self) -> None:
        """Test creating SuccessResponse with default values."""
        response = SuccessResponse()

        assert response.success is True
        assert response.message is None

    def test_success_response_with_message(self) -> None:
        """Test creating SuccessResponse with custom message."""
        response = SuccessResponse(message="Operation completed successfully")

        assert response.success is True
        assert response.message == "Operation completed successfully"

    def test_success_response_explicit_success_true(self) -> None:
        """Test creating SuccessResponse with explicit success=True."""
        response = SuccessResponse(success=True, message="All good")

        assert response.success is True
        assert response.message == "All good"

    def test_success_response_serialization_with_defaults(self) -> None:
        """Test SuccessResponse serialization with default values."""
        response = SuccessResponse()

        result = response.model_dump()

        assert result == {"success": True, "message": None}

    def test_success_response_serialization_with_message(self) -> None:
        """Test SuccessResponse serialization with message."""
        response = SuccessResponse(message="Query executed successfully")

        result = response.model_dump()

        assert result == {"success": True, "message": "Query executed successfully"}

    def test_success_response_serialization_exclude_none(self) -> None:
        """Test SuccessResponse serialization excluding None values."""
        response = SuccessResponse()

        result = response.model_dump(exclude_none=True)

        assert result == {"success": True}
        assert "message" not in result

    def test_success_response_from_dict(self) -> None:
        """Test creating SuccessResponse from dictionary."""
        data = {"success": True, "message": "Database updated"}

        response = SuccessResponse(**data)

        assert response.success is True
        assert response.message == "Database updated"

    def test_success_response_allows_success_false(self) -> None:
        """Test that SuccessResponse allows success=False (even if unusual)."""
        # While unusual for a "SuccessResponse", the model should allow it
        response = SuccessResponse(success=False, message="Not really a success")

        assert response.success is False
        assert response.message == "Not really a success"
