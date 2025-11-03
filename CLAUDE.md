# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A **Linkurious-compatible REST API** for Neo4j Enterprise multi-database instances built with FastAPI. The project follows **Specification-Driven Development** and **Test-Driven Development (TDD)** with a dual testing strategy: **pytest** for unit tests and **behave** for BDD acceptance tests.

**Key Constraint:** The API is **read-only** - all write operations (CREATE, DELETE, MERGE, SET, REMOVE) are blocked by query validation.

## Architecture

### Request Flow
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

### Directory Structure

```
neo4j-api/
├── specs/                  # API specifications (source of truth)
│   ├── endpoints-*.md      # Endpoint specifications
│   ├── authentication.md   # Auth specification
│   └── data-models.md      # Request/response models
│
├── features/               # BDD acceptance tests (Gherkin)
│   ├── *.feature           # 6 feature files, 92 scenarios
│   ├── steps/              # Step definitions (~100 reusable steps)
│   └── environment.py      # Test setup/teardown
│
├── app/                    # FastAPI application (NOT YET IMPLEMENTED)
│   ├── main.py             # FastAPI app with lifespan
│   ├── config.py           # Settings via pydantic-settings
│   ├── dependencies.py     # API key auth dependency
│   ├── routers/            # Endpoint routers
│   │   ├── health.py       # Health & databases
│   │   ├── search.py       # Node/edge search
│   │   ├── query.py        # Cypher execution
│   │   ├── nodes.py        # Node operations
│   │   └── schema.py       # Schema discovery
│   └── utils/
│       ├── neo4j_client.py # Neo4j driver wrapper
│       └── validators.py   # Query validation (read-only check)
│
└── tests/                  # Unit tests (pytest) (NOT YET IMPLEMENTED)
    ├── conftest.py         # Fixtures (client, mock_neo4j_driver, api_key)
    └── test_*.py           # Test files per router
```

### Key Architectural Decisions

1. **Specification-First:** All endpoint behavior is defined in `specs/` before implementation
2. **Multi-Database Routing:** Path parameter `{database}` routes to different Neo4j databases
3. **Read-Only Enforcement:** Query validator blocks write operations using keyword detection
4. **Linkurious Compatibility:** Response formats match Linkurious Enterprise API
5. **No Authentication on Health:** `/api/health` and `/api/databases` are public
6. **Mock-Based Testing:** BDD tests use mocks in `features/environment.py` until app is implemented

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# Or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your Neo4j credentials and API_KEY
```

### Running Tests

**Complete Test Suite:**
```bash
./scripts/run_all_tests.sh  # Unit + BDD + code quality
```

**BDD Tests Only:**
```bash
./scripts/run_bdd_tests.sh              # All BDD tests
./scripts/run_bdd_tests.sh --smoke      # Smoke tests only (~1 min)
./scripts/run_bdd_tests.sh --tag=auth   # Tests by tag
behave features/health.feature -v       # Single feature file
behave features/ --tags=@critical       # By tag directly
```

**Unit Tests (when implemented):**
```bash
pytest                                  # All tests
pytest tests/test_health.py -v          # Specific file
pytest -k "test_search" -v              # Pattern matching
pytest --cov=app --cov-report=html      # With coverage
```

**Single Test:**
```bash
pytest tests/test_health.py::test_health_check_success -v
```

### Code Quality
```bash
black app/ tests/ features/             # Format code
ruff check app/ tests/ features/        # Lint
mypy app/                               # Type check
```

### Development Server
```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Access API documentation
# http://localhost:8000/api/docs (Swagger UI)
# http://localhost:8000/api/redoc (ReDoc)
```

### Production Deployment
```bash
# Initial setup
./scripts/setup_production.sh

# Service management
sudo systemctl start neo4j-api
sudo systemctl stop neo4j-api
sudo systemctl restart neo4j-api
sudo systemctl status neo4j-api

# View logs
sudo journalctl -u neo4j-api -f

# Caddy
sudo systemctl reload caddy
caddy validate --config /etc/caddy/Caddyfile
```

## Development Workflow

### Specification-Driven + TDD Workflow

**CRITICAL:** This project follows a strict workflow. **Never commit directly to `main`.**

1. **Read Specification First**
   - Check `specs/endpoints-*.md` for endpoint behavior
   - Understand request/response models in `specs/data-models.md`
   - Review error cases in `specs/error-handling.md`

2. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

3. **Write BDD Feature (if new endpoint)**
   - Add Gherkin scenarios to appropriate `features/*.feature`
   - Use existing step definitions from `features/steps/`
   - Run: `behave features/your.feature --dry-run` to validate syntax

4. **Write Unit Tests First (RED)**
   - Create test file: `tests/test_your_feature.py`
   - Write failing tests based on specification
   - Run: `pytest tests/test_your_feature.py` (should FAIL)

5. **Implement Code (GREEN)**
   - Write minimal code to pass tests
   - Follow specification exactly
   - Run: `pytest tests/test_your_feature.py` (should PASS)

6. **Refactor**
   - Improve code quality while keeping tests green
   - Run: `black`, `ruff`, `mypy`

7. **Verify All Tests Pass**
   ```bash
   ./scripts/run_all_tests.sh
   ```

8. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature with tests"
   git push origin feature/your-feature-name
   ```

9. **Create Pull Request**
   - Title: Use conventional commits (`feat:`, `fix:`, `test:`, `refactor:`)
   - Description: What, why, testing notes
   - Wait for CI to pass (GitHub Actions)
   - Request review

10. **After Approval: Squash and Merge**

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `test:` Adding tests
- `refactor:` Code refactoring
- `docs:` Documentation changes
- `chore:` Maintenance tasks

## BDD Testing Strategy

### Feature Files and Tags

**6 feature files with 92 scenarios:**
- `health.feature` - Health & database endpoints
- `authentication.feature` - API key auth
- `search.feature` - Node/edge search
- `query.feature` - Cypher execution (read-only validation)
- `nodes.feature` - Node operations
- `schema.feature` - Schema discovery

**Common tags for selective execution:**
- `@smoke` - Critical smoke tests (run first)
- `@critical` - High-priority tests
- `@error` - Error handling tests
- `@auth`, `@search`, `@query`, `@nodes`, `@schema` - By feature area
- `@database` - Multi-database tests
- `@performance` - Performance tests

**Example: Run smoke tests**
```bash
behave features/ --tags=@smoke
```

### Step Definition Organization

Reusable steps are organized by concern:

- **`http_steps.py`** - HTTP requests, response validation, JSON checks, error validation
- **`common_steps.py`** - Array validation, field checks, general assertions
- **`auth_steps.py`** - Authentication setup and validation
- **`neo4j_steps.py`** - Database state setup, search operations, query execution

**When writing new scenarios:** Check existing step definitions first before creating new ones.

### Mock Test Client

Until the FastAPI app is fully implemented, BDD tests use mocks in `features/environment.py`:

- `create_test_client()` - Returns mock HTTP client
- `create_mock_response()` - Simulates API responses based on scenario state
- Tests validate **behavior** against **specifications**, not actual implementation

## Important Testing Patterns

### Testing API Key Authentication

```python
# Unit test pattern
def test_valid_api_key_allows_access(client, mock_neo4j_driver, api_key):
    response = client.get(
        "/api/neo4j/graph/nodes/count",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200

# BDD pattern (Gherkin)
Scenario: Valid API key allows access
  Given the Neo4j database is connected
  When I send a GET request to "/api/neo4j/graph/nodes/count" with authentication
  Then the response status code should be 200
```

### Testing Read-Only Query Validation

**Critical security feature:** All Cypher queries must be validated.

```python
# Validator test pattern
from app.utils.validators import is_read_only_query

def test_create_query_is_blocked():
    assert is_read_only_query("CREATE (n:Person) RETURN n") is False

def test_match_query_is_allowed():
    assert is_read_only_query("MATCH (n) RETURN n") is True
```

**Forbidden keywords:** CREATE, DELETE, MERGE, SET, REMOVE, DROP
**Allowed patterns:** MATCH, RETURN, CALL db.*, SHOW, WITH, OPTIONAL MATCH

### Testing Multi-Database Routing

```python
def test_database_routing(client, api_key):
    # Test accessing different databases via path parameter
    response1 = client.get(
        "/api/neo4j/graph/nodes/count",
        headers={"X-API-Key": api_key}
    )
    response2 = client.get(
        "/api/investigation_001/graph/nodes/count",
        headers={"X-API-Key": api_key}
    )
    # Both should work, routing to different Neo4j databases
```

## Coverage Requirements

- **Overall:** 80% minimum
- **Routers:** 90%+
- **Validators:** 100% (critical for security)
- **Utils:** 85%+

**Check coverage:**
```bash
pytest --cov=app --cov-report=term --cov-report=html
# Open htmlcov/index.html
```

## Common Pitfalls

1. **Don't mock FastAPI dependencies in unit tests** - Use `TestClient` with dependency overrides
2. **Always validate against specs** - Implementation must match `specs/endpoints-*.md` exactly
3. **Mock Neo4j driver, not FastAPI** - Use `@patch('app.utils.neo4j_client.GraphDatabase.driver')`
4. **Read-only validation is critical** - Never skip query validation tests
5. **Public endpoints** - `/api/health` and `/api/databases` must NOT require authentication
6. **Linkurious format** - Response structure must match Linkurious API (see `specs/data-models.md`)

## Project Status

**Current state:** Specifications and BDD test framework complete. FastAPI implementation pending.

**Implementation order (from `IMPLEMENTATION_PLAN.md`):**
1. Health endpoints (`feature/health-endpoints`)
2. Authentication (`feature/api-key-auth`)
3. Search endpoints (`feature/search-endpoints`)
4. Query execution (`feature/query-execution`)
5. Node operations (`feature/node-operations`)
6. Schema endpoints (`feature/schema-endpoints`)
7. Deployment (`deployment/caddy-setup`)

## Key Files to Reference

- **`specs/README.md`** - Specification-driven development process
- **`features/README.md`** - Comprehensive BDD testing guide
- **`IMPLEMENTATION_PLAN.md`** - Detailed TDD implementation plan with examples
- **`BDD_SETUP_SUMMARY.md`** - BDD framework overview
- **`README.md`** - Project overview and quick start
