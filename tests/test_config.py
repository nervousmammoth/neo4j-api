"""Unit tests for app.config module.

Tests configuration loading from environment variables and .env file
using pydantic-settings.
"""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from app.config import Settings, get_settings


class TestSettingsValidEnvironment:
    """Test Settings class with valid environment variables."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up valid environment variables for all tests."""
        # Clear lru_cache before each test
        get_settings.cache_clear()

        # Neo4j settings
        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "password123")
        monkeypatch.setenv("NEO4J_DATABASE", "neo4j")

        # API settings
        monkeypatch.setenv("API_KEY", "test-api-key-12345")

    def test_settings_loads_from_environment(self) -> None:
        """Test that Settings loads values from environment variables."""
        settings = Settings()

        assert settings.neo4j_uri == "bolt://localhost:7687"
        assert settings.neo4j_username == "neo4j"
        assert settings.neo4j_password.get_secret_value() == "password123"
        assert settings.neo4j_database == "neo4j"
        assert settings.api_key.get_secret_value() == "test-api-key-12345"

    def test_settings_uses_default_values(self) -> None:
        """Test that optional settings use default values."""
        settings = Settings()

        # Neo4j defaults
        assert settings.neo4j_max_connection_lifetime == 3600
        assert settings.neo4j_max_connection_pool_size == 50
        assert settings.neo4j_connection_timeout == 30

        # API defaults
        assert settings.api_title == "Neo4j API"
        assert settings.api_version == "1.0.0"
        assert settings.api_prefix == "/api"

        # Server defaults
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.workers == 4
        assert settings.reload is False
        assert settings.log_level == "info"
        assert settings.environment == "development"

    def test_settings_overrides_defaults_with_env_vars(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that environment variables override default values."""
        monkeypatch.setenv("NEO4J_MAX_CONNECTION_LIFETIME", "7200")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("WORKERS", "8")
        monkeypatch.setenv("LOG_LEVEL", "debug")

        settings = Settings()

        assert settings.neo4j_max_connection_lifetime == 7200
        assert settings.port == 9000
        assert settings.workers == 8
        assert settings.log_level == "debug"

    def test_secret_str_fields_are_hidden(self) -> None:
        """Test that SecretStr fields are hidden in repr."""
        settings = Settings()
        settings_repr = repr(settings)

        # Secrets should not appear in repr
        assert "password123" not in settings_repr
        assert "test-api-key-12345" not in settings_repr

        # But we can access them via get_secret_value()
        assert settings.neo4j_password.get_secret_value() == "password123"
        assert settings.api_key.get_secret_value() == "test-api-key-12345"


class TestSettingsValidation:
    """Test Settings field validation."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up minimal valid environment variables."""
        get_settings.cache_clear()

        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "password123")
        monkeypatch.setenv("API_KEY", "test-api-key")

    @pytest.mark.parametrize(
        "uri",
        [
            "bolt://localhost:7687",
            "bolt+s://localhost:7687",
            "bolt+ssc://localhost:7687",
            "neo4j://localhost:7687",
            "neo4j+s://localhost:7687",
            "neo4j+ssc://localhost:7687",
        ],
    )
    def test_valid_uri_schemes_accepted(
        self, monkeypatch: pytest.MonkeyPatch, uri: str
    ) -> None:
        """Test that valid bolt:// and neo4j:// URI schemes are accepted."""
        monkeypatch.setenv("NEO4J_URI", uri)
        settings = Settings()
        assert settings.neo4j_uri == uri

    def test_invalid_uri_scheme_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid URI scheme is rejected."""
        invalid_uris = [
            "http://localhost:7687",
            "https://localhost:7687",
            "localhost:7687",
            "tcp://localhost:7687",
        ]

        for uri in invalid_uris:
            monkeypatch.setenv("NEO4J_URI", uri)
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(
                "Neo4j URI must start with bolt:// or neo4j:// scheme" in str(error)
                for error in errors
            )

    def test_valid_log_levels_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that valid log levels are accepted."""
        valid_levels = ["debug", "info", "warning", "error", "critical"]

        for level in valid_levels:
            monkeypatch.setenv("LOG_LEVEL", level)
            settings = Settings()
            assert settings.log_level == level.lower()

    def test_log_level_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that log level validation is case insensitive."""
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        settings = Settings()
        assert settings.log_level == "info"

        monkeypatch.setenv("LOG_LEVEL", "DeBuG")
        get_settings.cache_clear()
        settings = Settings()
        assert settings.log_level == "debug"

    def test_invalid_log_level_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid log level is rejected."""
        invalid_levels = ["trace", "verbose", "fatal", "invalid"]

        for level in invalid_levels:
            monkeypatch.setenv("LOG_LEVEL", level)
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any("Log level must be one of:" in str(error) for error in errors)

    def test_port_range_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that port must be between 1 and 65535."""
        # Valid ports
        valid_ports = ["1", "8000", "65535"]
        for port in valid_ports:
            monkeypatch.setenv("PORT", port)
            settings = Settings()
            assert settings.port == int(port)

        # Invalid ports
        invalid_ports = ["0", "-1", "65536", "99999"]
        for port in invalid_ports:
            monkeypatch.setenv("PORT", port)
            with pytest.raises(ValidationError):
                Settings()

    def test_positive_integer_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that connection pool settings must be positive integers."""
        # Test neo4j_max_connection_lifetime
        monkeypatch.setenv("NEO4J_MAX_CONNECTION_LIFETIME", "0")
        with pytest.raises(ValidationError):
            Settings()

        monkeypatch.setenv("NEO4J_MAX_CONNECTION_LIFETIME", "-1")
        with pytest.raises(ValidationError):
            Settings()

        # Test neo4j_max_connection_pool_size
        monkeypatch.setenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "0")
        with pytest.raises(ValidationError):
            Settings()

        # Test neo4j_connection_timeout
        monkeypatch.setenv("NEO4J_CONNECTION_TIMEOUT", "-5")
        with pytest.raises(ValidationError):
            Settings()

        # Test workers
        monkeypatch.setenv("WORKERS", "0")
        with pytest.raises(ValidationError):
            Settings()


class TestSettingsMissingRequired:
    """Test Settings with missing required fields."""

    @pytest.fixture(autouse=True)
    def clear_cache(self) -> None:
        """Clear lru_cache before each test."""
        get_settings.cache_clear()

    def test_missing_neo4j_uri_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing NEO4J_URI raises ValidationError."""
        monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "password")
        monkeypatch.setenv("API_KEY", "key")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("neo4j_uri",) for error in errors)

    def test_missing_neo4j_username_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing NEO4J_USERNAME raises ValidationError."""
        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_PASSWORD", "password")
        monkeypatch.setenv("API_KEY", "key")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("neo4j_username",) for error in errors)

    def test_missing_neo4j_password_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing NEO4J_PASSWORD raises ValidationError."""
        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
        monkeypatch.setenv("API_KEY", "key")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("neo4j_password",) for error in errors)

    def test_missing_api_key_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing API_KEY raises ValidationError."""
        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "password")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("api_key",) for error in errors)


class TestGetSettingsFunction:
    """Test get_settings() singleton function."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up valid environment variables."""
        get_settings.cache_clear()

        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "password123")
        monkeypatch.setenv("API_KEY", "test-api-key")

    def test_get_settings_returns_settings_instance(self) -> None:
        """Test that get_settings() returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_returns_cached_instance(self) -> None:
        """Test that get_settings() returns the same cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the exact same object (singleton pattern)
        assert settings1 is settings2

    def test_cache_clear_creates_new_instance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that clearing cache creates a new Settings instance."""
        settings1 = get_settings()

        # Clear cache and change environment
        get_settings.cache_clear()
        monkeypatch.setenv("PORT", "9000")

        settings2 = get_settings()

        # Should be different objects with different values
        assert settings1 is not settings2
        assert settings1.port == 8000
        assert settings2.port == 9000


class TestSettingsEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up minimal valid environment variables."""
        get_settings.cache_clear()

        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "password123")
        monkeypatch.setenv("API_KEY", "test-api-key")

    def test_empty_string_values_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that empty string values are rejected for required fields."""
        monkeypatch.setenv("NEO4J_URI", "")
        with pytest.raises(ValidationError):
            Settings()

        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        monkeypatch.setenv("NEO4J_USERNAME", "")
        with pytest.raises(ValidationError):
            Settings()

    def test_empty_api_key_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that empty API key is rejected."""
        monkeypatch.setenv("API_KEY", "")
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any("API key cannot be empty" in str(error) for error in errors)

    def test_whitespace_api_key_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that whitespace-only API key is rejected."""
        whitespace_keys = ["   ", "\t", "\n", "  \t\n  "]

        for key in whitespace_keys:
            monkeypatch.setenv("API_KEY", key)
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any("API key cannot be empty" in str(error) for error in errors)

    def test_boundary_values_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that boundary values are correctly handled."""
        # Minimum valid values
        monkeypatch.setenv("PORT", "1")
        monkeypatch.setenv("WORKERS", "1")
        monkeypatch.setenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "1")
        monkeypatch.setenv("NEO4J_CONNECTION_TIMEOUT", "1")

        settings = Settings()
        assert settings.port == 1
        assert settings.workers == 1
        assert settings.neo4j_max_connection_pool_size == 1
        assert settings.neo4j_connection_timeout == 1

        # Maximum valid port
        monkeypatch.setenv("PORT", "65535")
        get_settings.cache_clear()
        settings = Settings()
        assert settings.port == 65535

    def test_boolean_reload_field(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that reload boolean field works correctly."""
        # Test true values
        for value in ["true", "True", "TRUE", "1", "yes"]:
            monkeypatch.setenv("RELOAD", value)
            get_settings.cache_clear()
            settings = Settings()
            assert settings.reload is True

        # Test false values
        for value in ["false", "False", "FALSE", "0", "no"]:
            monkeypatch.setenv("RELOAD", value)
            get_settings.cache_clear()
            settings = Settings()
            assert settings.reload is False

    def test_case_insensitive_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables are case insensitive."""
        monkeypatch.setenv("neo4j_uri", "bolt://localhost:7687")
        monkeypatch.setenv("Neo4j_Username", "neo4j")
        monkeypatch.setenv("NEO4J_PASSWORD", "password")
        monkeypatch.setenv("api_key", "key")

        settings = Settings()
        assert settings.neo4j_uri == "bolt://localhost:7687"
        assert settings.neo4j_username == "neo4j"
