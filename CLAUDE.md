# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A **Linkurious-compatible REST API** for Neo4j Enterprise multi-database instances built with FastAPI. The API is **read-only** - all write operations (CREATE, DELETE, MERGE, SET, REMOVE) are blocked by query validation.

**Development approach:** Specification-Driven Development + TDD with 100% coverage enforcement.

## Quick Reference Commands

```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
./scripts/setup_hooks.sh

# Run tests
pytest                                          # All tests
pytest tests/test_health.py -v                  # Single file
pytest tests/test_health.py::test_name -v       # Single test
pytest -k "search" -v                           # Pattern match
pytest --cov=app --cov-report=term-missing      # With coverage

# Code quality
black app/ tests/                               # Format
ruff check app/ tests/ --fix                    # Lint + fix
mypy app/                                       # Type check
pre-commit run --all-files                      # All checks

# Development server
uvicorn app.main:app --reload
# Docs: http://localhost:8000/api/docs

# Full test suite (before push)
./scripts/run_all_tests.sh
```

## Architecture

```
Client → Caddy (:80) → FastAPI (:8000) → Neo4j (:7687)
                ↓
         X-API-Key validation
                ↓
         Database routing (/api/{database}/...)
                ↓
         Query validation (read-only check)
                ↓
         Neo4j driver with multi-database support
```

**Key files:**
- `specs/` - API specifications (source of truth for all endpoint behavior)
- `app/config.py` - Settings via pydantic-settings
- `app/dependencies.py` - API key auth dependency
- `app/utils/neo4j_client.py` - Neo4j driver wrapper
- `app/utils/validators.py` - Query validation (read-only enforcement)
- `app/routers/` - Endpoint implementations
- `tests/conftest.py` - Shared fixtures (client, mock_neo4j_driver, api_key)

## Development Workflow

**Never commit directly to `main`.** Follow TDD:

1. Read spec in `specs/endpoints-*.md`
2. Create branch: `git checkout -b issue/XX-description`
3. Write failing tests (RED)
4. Implement minimal code (GREEN)
5. Refactor, run quality checks
6. Push and create PR with `gh pr create`

**Commit format:** `type(issue-XX): description` (types: feat, fix, test, refactor, docs, chore)

## Testing Patterns

### Mock Neo4j driver (not FastAPI)
```python
@patch('app.utils.neo4j_client.GraphDatabase.driver')
def test_something(mock_driver, client, api_key):
    # Configure mock
    mock_driver.return_value.verify_connectivity.return_value = None
```

### API key authentication
```python
def test_protected_endpoint(client, api_key):
    response = client.get("/api/neo4j/graph/nodes/count", headers={"X-API-Key": api_key})
    assert response.status_code == 200
```

### Read-only query validation
```python
from app.utils.validators import is_read_only_query

def test_write_blocked():
    assert is_read_only_query("CREATE (n) RETURN n") is False
    assert is_read_only_query("MATCH (n) RETURN n") is True
```

**Forbidden keywords:** CREATE, DELETE, MERGE, SET, REMOVE, DROP

## Critical Rules

1. **Specifications are source of truth** - Check `specs/endpoints-*.md` before implementing
2. **100% test coverage required** - Enforced by pre-push hooks
3. **Public endpoints:** `/api/health` and `/api/databases` - NO authentication
4. **Protected endpoints:** All others require `X-API-Key` header
5. **Response formats must match Linkurious API** - See `specs/data-models.md`
6. **Use `TestClient` with dependency overrides** - Don't mock FastAPI dependencies directly

## Issue Tracking

Issues in `issues/` directory, numbered `XX-description.md`. Completed issues move to `issues/completed/`.

```bash
ls issues/*.md                    # Active issues
ls issues/completed/              # Completed
mv issues/XX-*.md issues/completed/  # After merge
```

## Key Specs to Reference

- `specs/data-models.md` - Request/response formats
- `specs/authentication.md` - X-API-Key header validation
- `specs/error-handling.md` - Error response structure
- `specs/endpoints-*.md` - Individual endpoint specifications
