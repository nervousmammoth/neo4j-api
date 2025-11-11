"""Application configuration and settings.

This module provides configuration management using pydantic-settings,
loading values from environment variables and .env files.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # type: ignore[misc]
    """Application settings loaded from environment variables.

    Settings are loaded from environment variables and .env file.
    Environment variables take precedence over .env file values.
    """

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
            ValueError: If URI is empty or doesn't start with bolt:// or neo4j:// scheme.
        """
        if not v or not v.strip():
            raise ValueError("Neo4j URI cannot be empty")
        if not v.startswith(
            (
                "bolt://",
                "bolt+s://",
                "bolt+ssc://",
                "neo4j://",
                "neo4j+s://",
                "neo4j+ssc://",
            )
        ):
            raise ValueError("Neo4j URI must start with bolt:// or neo4j:// scheme")
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
        if not v or not v.strip():
            raise ValueError("Neo4j username cannot be empty")
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
        valid_levels = {"debug", "info", "warning", "error", "critical"}
        if v.lower() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.lower()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance loaded from environment.
    """
    return Settings()
