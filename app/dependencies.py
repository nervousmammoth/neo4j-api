"""FastAPI dependency injection functions.

This module provides dependencies for authentication, database connections,
and other cross-cutting concerns.
"""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException

from app.config import Settings, get_settings


async def verify_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),  # noqa: B008
) -> None:
    """Verify API key from X-API-Key header.

    This dependency validates the API key provided in the request header
    against the configured API key. It returns structured error responses
    following the ErrorResponse model format.

    Args:
        x_api_key: API key from request header (case-insensitive header name).
        settings: Application settings with configured API key.

    Raises:
        HTTPException: If API key is missing or invalid (403 Forbidden).

    Returns:
        None: Dependency succeeds silently if API key is valid.

    Note:
        - Header name (X-API-Key) is case-insensitive (FastAPI handles this)
        - API key value comparison is case-sensitive
        - Returns 403 Forbidden (not 401) per API specifications
        - Error responses use structured format with code/message/details
    """
    # Check if API key is missing, empty, or whitespace-only
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "MISSING_API_KEY",
                    "message": "API key is required",
                    "details": {"header": "X-API-Key"},
                }
            },
        )

    # Check if API key matches configured value (case-sensitive, constant-time)
    if not secrets.compare_digest(x_api_key, settings.api_key.get_secret_value()):
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid API key provided",
                    "details": {},
                }
            },
        )

    # API key is valid - return None (dependency succeeds)
    return None
