"""Application configuration and settings.

This module provides configuration management using pydantic-settings,
loading values from environment variables and .env files.
"""

from __future__ import annotations

from functools import lru_cache
from typing import ClassVar
from urllib.parse import urlparse

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # type: ignore[misc]
    """Application settings loaded from environment variables.

    Settings are loaded from environment variables and .env file.
    Environment variables take precedence over .env file values.
    """

    # Valid log levels
    _VALID_LOG_LEVELS: ClassVar[set[str]] = {
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    }

    # Neo4j Connection
    neo4j_uri: str = Field(..., description="Neo4j connection URI")
    neo4j_username: str = Field(..., description="Neo4j username")
    neo4j_password: SecretStr = Field(..., description="Neo4j password")
    neo4j_database: str = Field(default="neo4j", description="Default database")
    neo4j_max_connection_lifetime: int = Field(default=3600, ge=1)
    neo4j_max_connection_pool_size: int = Field(default=50, ge=1)
    neo4j_connection_timeout: int = Field(default=30, ge=1)

    # API Configuration
    api_key: SecretStr = Field(..., description="API authentication key")
    api_title: str = Field(default="Neo4j API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_prefix: str = Field(default="/api", description="API URL prefix")

    # Server Configuration
    host: str = Field(
        default="0.0.0.0",  # noqa: S104  # nosec B104
        description="Server host",
    )
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=4, ge=1, description="Worker processes")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    log_level: str = Field(default="info", description="Logging level")
    environment: str = Field(default="development", description="Environment name")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("neo4j_uri")
    @classmethod
    def validate_neo4j_uri(cls, v: str) -> str:
        """Validate Neo4j URI format.

        Args:
            v: The Neo4j URI to validate.

        Returns:
            The validated URI.

        Raises:
            ValueError: If URI is empty, has invalid scheme, no host, or invalid port.
        """
        if not v.strip():
            raise ValueError("Neo4j URI cannot be empty")

        valid_schemes = ("bolt", "bolt+s", "bolt+ssc", "neo4j", "neo4j+s", "neo4j+ssc")

        try:
            parsed = urlparse(v)
            if parsed.scheme not in valid_schemes:
                raise ValueError(
                    f"Neo4j URI must use one of: {', '.join(valid_schemes)}"
                )
            if not parsed.netloc:
                raise ValueError("Neo4j URI must include a host")

            # Validate port if colon is present
            if ":" in parsed.netloc:
                try:
                    port = parsed.port
                    if port is None:
                        # Colon present but no port number
                        raise ValueError(
                            "Invalid Neo4j URI format: port number missing after ':'"
                        )
                    if not (1 <= port <= 65535):
                        raise ValueError("Neo4j URI port must be between 1 and 65535")
                except ValueError as port_error:
                    # urlparse raises ValueError for invalid ports (e.g., > 65535)
                    if "Port out of range" in str(port_error):
                        raise ValueError(
                            "Neo4j URI port must be between 1 and 65535"
                        ) from port_error
                    raise
        except ValueError:
            # Re-raise ValueError messages
            raise
        except Exception as e:  # pragma: no cover
            # Catch any unexpected exceptions from urlparse (defensive programming)
            raise ValueError(f"Invalid Neo4j URI format: {e}") from e

        return v

    @field_validator("neo4j_username")
    @classmethod
    def validate_neo4j_username(cls, v: str) -> str:
        """Validate Neo4j username is not empty.

        Args:
            v: The Neo4j username to validate.

        Returns:
            The validated username.

        Raises:
            ValueError: If username is empty.
        """
        if not v.strip():
            raise ValueError("Neo4j username cannot be empty")
        return v

    @field_validator("neo4j_password")
    @classmethod
    def validate_neo4j_password(cls, v: SecretStr) -> SecretStr:
        """Validate Neo4j password is not empty.

        Args:
            v: The Neo4j password to validate.

        Returns:
            The validated password.

        Raises:
            ValueError: If password is empty or contains only whitespace.
        """
        if not v.get_secret_value().strip():
            raise ValueError("Neo4j password cannot be empty")
        return v

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """Validate API key is not empty.

        Args:
            v: The API key to validate.

        Returns:
            The validated API key.

        Raises:
            ValueError: If API key is empty or contains only whitespace.
        """
        if not v.get_secret_value().strip():
            raise ValueError("API key cannot be empty")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level.

        Args:
            v: The log level to validate.

        Returns:
            The validated log level in lowercase.

        Raises:
            ValueError: If log level is not one of the valid levels.
        """
        if v.lower() not in cls._VALID_LOG_LEVELS:
            raise ValueError(f"Log level must be one of: {cls._VALID_LOG_LEVELS}")
        return v.lower()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance loaded from environment.
    """
    return Settings()
