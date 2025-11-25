"""Pydantic models for request and response data.

This module contains all data models following Linkurious API format.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Error(BaseModel):
    """Error details structure.

    Used within ErrorResponse to provide detailed error information.

    Attributes:
        code: Machine-readable error code (e.g., "NODE_NOT_FOUND", "VALIDATION_ERROR").
        message: Human-readable error message describing what went wrong.
        details: Optional additional context or metadata about the error.

    Examples:
        >>> error = Error(
        ...     code="NODE_NOT_FOUND",
        ...     message="Node with ID '12345' not found",
        ...     details={"node_id": "12345", "database": "neo4j"}
        ... )
        >>> error.code
        'NODE_NOT_FOUND'
        >>> error.model_dump()
        {'code': 'NODE_NOT_FOUND', 'message': "Node with ID '12345' not found", 'details': {'node_id': '12345', 'database': 'neo4j'}}
    """

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        default=None, description="Optional additional error details"
    )


class ErrorResponse(BaseModel):
    """Standard error response wrapper.

    Used for all error responses across the API following Linkurious API format.
    The error field contains a nested Error object with code, message, and optional details.

    Attributes:
        error: Nested Error object containing error details.

    Examples:
        >>> error_obj = Error(
        ...     code="WRITE_OPERATION_FORBIDDEN",
        ...     message="Write operations are not allowed",
        ...     details={"forbidden_keyword": "CREATE"}
        ... )
        >>> response = ErrorResponse(error=error_obj)
        >>> response.model_dump()
        {'error': {'code': 'WRITE_OPERATION_FORBIDDEN', 'message': 'Write operations are not allowed', 'details': {'forbidden_keyword': 'CREATE'}}}
    """

    error: Error = Field(..., description="Error details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": {
                    "code": "NODE_NOT_FOUND",
                    "message": "Node with ID '12345' not found",
                    "details": {"node_id": "12345", "database": "neo4j"},
                }
            }
        }
    }


class SuccessResponse(BaseModel):
    """Generic success response for simple operations.

    Used for simple success responses without data payload.
    For operations that return data, use domain-specific response models instead.

    Attributes:
        success: Success indicator (typically True for success responses).
        message: Optional success message providing additional context.

    Examples:
        >>> response = SuccessResponse()
        >>> response.success
        True
        >>> response = SuccessResponse(message="Operation completed successfully")
        >>> response.model_dump()
        {'success': True, 'message': 'Operation completed successfully'}
    """

    success: Literal[True] = Field(default=True, description="Success indicator")
    message: str | None = Field(default=None, description="Optional success message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response.

    Response model for the GET /api/health endpoint.
    Returns API health status and Neo4j connectivity information.

    Attributes:
        status: Overall health status ("healthy" or "unhealthy").
        neo4j: Neo4j connection status ("connected" or "disconnected").
        version: API version string.
        error: Optional error message when unhealthy.

    Examples:
        >>> # Healthy response
        >>> response = HealthResponse(
        ...     status="healthy",
        ...     neo4j="connected",
        ...     version="1.0.0"
        ... )
        >>> response.model_dump()
        {'status': 'healthy', 'neo4j': 'connected', 'version': '1.0.0', 'error': None}

        >>> # Unhealthy response
        >>> response = HealthResponse(
        ...     status="unhealthy",
        ...     neo4j="disconnected",
        ...     version="1.0.0",
        ...     error="Connection refused"
        ... )
    """

    status: Literal["healthy", "unhealthy"] = Field(
        ..., description="Overall health status"
    )
    neo4j: Literal["connected", "disconnected"] = Field(
        ..., description="Neo4j connection status"
    )
    version: str | None = Field(default=None, description="API version")
    error: str | None = Field(default=None, description="Error message when unhealthy")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "neo4j": "connected",
                    "version": "1.0.0",
                },
                {
                    "status": "unhealthy",
                    "neo4j": "disconnected",
                    "version": "1.0.0",
                    "error": "Connection refused to bolt://localhost:7687",
                },
            ]
        }
    }


# Additional domain-specific models will be added in later issues (13, 17, 21, 26)
