# Issue 04: Implement Configuration Module

## Status
⏳ **TODO**

**Estimated Time:** 2 hours
**Branch:** `issue/04-config-module`
**Phase:** 1 - Core Infrastructure

## Description
Implement `app/config.py` using pydantic-settings for environment variable management. This module provides centralized configuration for Neo4j connection, API settings, and application behavior.

## Related Specifications
- [ ] **Spec file:** `specs/api-overview.md` - Configuration requirements
- [ ] **Spec file:** `specs/authentication.md` - API key configuration
- [ ] **Reference:** `.env.example` - Environment variables template

## Related BDD Tests
N/A - Configuration module tested through unit tests only

## Dependencies
- [ ] Issue #01 - .env.example must exist
- [ ] Issue #02 - App structure must exist

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Create test file: `tests/test_config.py`
- [ ] Write unit tests for Settings model
  - [ ] Test loading from environment variables
  - [ ] Test default values
  - [ ] Test validation (e.g., URI format)
  - [ ] Test missing required variables
  - [ ] Test Neo4j connection settings
  - [ ] Test API configuration settings
- [ ] Run tests: `pytest tests/test_config.py -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Create implementation file: `app/config.py`
- [ ] Implement Settings class with pydantic-settings
  - [ ] Add Neo4j connection fields
  - [ ] Add API authentication fields
  - [ ] Add server configuration fields
  - [ ] Add field validators
  - [ ] Add model configuration for .env loading
- [ ] Create get_settings() function
- [ ] Run tests: `pytest tests/test_config.py -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR - Improve Code Quality
- [ ] Run black: `black app/ tests/`
- [ ] Run ruff: `ruff check app/ tests/ --fix`
- [ ] Run mypy: `mypy app/`
- [ ] **Verify tests still pass** ✅

### 4️⃣ BDD Validation (if applicable)
N/A - Configuration tested through unit tests

### 5️⃣ Coverage Check
- [ ] Run coverage: `pytest --cov=app.config --cov-report=term-missing --cov-report=html`
- [ ] **Verify 100% coverage** for new code ✅
- [ ] Check HTML report: `open htmlcov/index.html`

---

## Acceptance Criteria

### Functional Requirements
- [ ] Settings class implemented with pydantic-settings
- [ ] All Neo4j connection settings configurable
- [ ] API_KEY configuration present
- [ ] Default values for optional settings
- [ ] Field validation for critical settings
- [ ] get_settings() function returns singleton instance
- [ ] Loads from .env file automatically
- [ ] Environment variables override .env values

### Non-Functional Requirements
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage for new code
- [ ] Type hints present (mypy compliant)
- [ ] Code formatted (black)
- [ ] Linting passed (ruff)
- [ ] No security issues (bandit)
- [ ] Documentation updated (docstrings)

### Code Quality Gates
- [ ] Pre-commit hooks pass
- [ ] All pytest tests pass
- [ ] Coverage >= 100% for new code
- [ ] No mypy errors
- [ ] No ruff warnings

---

## Implementation Notes

### Files to Create
```
app/config.py
tests/test_config.py
```

### Key Implementation Details

**app/config.py structure:**
- Use `pydantic_settings.BaseSettings` as base class
- Use `model_config` with `env_file=".env"` and `env_file_encoding="utf-8"`
- Group settings by concern (Neo4j, API, Server)
- Provide sensible defaults for optional values
- Add field validators for URI format, positive integers, etc.

**Settings to include:**
1. **Neo4j Connection:**
   - `neo4j_uri: str` (required)
   - `neo4j_username: str` (required)
   - `neo4j_password: SecretStr` (required, hidden in logs)
   - `neo4j_database: str` (default: "neo4j")
   - `neo4j_max_connection_lifetime: int` (default: 3600)
   - `neo4j_max_connection_pool_size: int` (default: 50)
   - `neo4j_connection_timeout: int` (default: 30)

2. **API Configuration:**
   - `api_key: SecretStr` (required, hidden in logs)
   - `api_title: str` (default: "Neo4j API")
   - `api_version: str` (default: "1.0.0")
   - `api_prefix: str` (default: "/api")

3. **Server Configuration:**
   - `host: str` (default: "0.0.0.0")
   - `port: int` (default: 8000)
   - `workers: int` (default: 4)
   - `reload: bool` (default: False)
   - `log_level: str` (default: "info")
   - `environment: str` (default: "development")

### Example Code Structure

```python
"""Application configuration and settings.

This module provides configuration management using pydantic-settings,
loading values from environment variables and .env files.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    host: str = Field(default="0.0.0.0", description="Server host")
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
        """Validate Neo4j URI format."""
        if not v.startswith(("bolt://", "bolt+s://", "bolt+ssc://", "neo4j://", "neo4j+s://", "neo4j+ssc://")):
            raise ValueError("Neo4j URI must start with bolt:// or neo4j:// scheme")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
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
```

### Testing Strategy

**Unit tests:**
- Test Settings instantiation with environment variables
- Test default values when optional variables not set
- Test field validation (URI format, port range, log level)
- Test SecretStr fields are hidden in repr
- Test missing required fields raises ValidationError
- Mock environment variables using monkeypatch fixture

**Mocking approach:**
- Use pytest's `monkeypatch` fixture to set environment variables
- Clear lru_cache between tests to ensure fresh settings
- Test both .env file loading and environment variable override

**Edge cases:**
- Invalid Neo4j URI format
- Invalid port number (< 1 or > 65535)
- Invalid log level
- Missing required fields
- Empty string values
- Negative connection pool sizes

---

## Git Workflow

### Start Issue
```bash
git checkout main
git pull origin main
git checkout -b issue/04-config-module
```

### During Development
```bash
# TDD Cycle: Write tests first
# Create tests/test_config.py
# Run pytest tests/test_config.py -v (should FAIL)

# Implement app/config.py
# Run pytest tests/test_config.py -v (should PASS)

# Refactor
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# Verify coverage
pytest tests/test_config.py --cov=app.config --cov-report=term-missing

# Commit (pre-commit hooks run automatically)
git add app/config.py tests/test_config.py
git commit -m "feat(issue-04): implement configuration module with pydantic-settings"

# Push
git push origin issue/04-config-module
```

### Create Pull Request
```bash
gh pr create \
  --title "feat: implement configuration module" \
  --body "$(cat <<'EOF'
## Summary
- Implemented app/config.py with pydantic-settings
- Added comprehensive unit tests with 100% coverage
- Supports .env file and environment variable configuration

## Changes
- Created Settings class with all required configuration fields
- Added field validators for Neo4j URI, port, log level
- Implemented get_settings() singleton function
- Full test coverage with edge case handling

## Testing
- [x] Unit tests pass (pytest)
- [x] 100% coverage achieved
- [x] Pre-commit hooks pass
- [x] Type checking passes (mypy)

## Closes
Closes #04

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### After Merge
```bash
# Move ticket to completed
mv issues/04-config-module.md issues/completed/

# Update local main
git checkout main
git pull origin main
```

---

## Verification Commands

```bash
# Run unit tests
pytest tests/test_config.py -v

# Run with coverage
pytest tests/test_config.py --cov=app.config --cov-report=term-missing

# Run type checking
mypy app/config.py

# Run all quality checks
pre-commit run --all-files

# Test loading settings
python -c "from app.config import get_settings; print(get_settings())"
```

---

## References
- **Pydantic Settings:** https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **Environment file:** `.env.example`
- **Specification:** `specs/api-overview.md`
- **Implementation Plan:** `IMPLEMENTATION_PLAN.md` - Phase 1

---

## Notes
- Use `SecretStr` for sensitive fields (passwords, API keys) to prevent logging
- Use `lru_cache` on get_settings() for singleton pattern
- Field validators ensure configuration is valid at startup
- Settings are immutable after creation (frozen=False but should not be modified)
- The `case_sensitive=False` allows flexible environment variable naming
- This module is used by all other modules requiring configuration
