# Implementation Plan: Neo4j Multi-Database REST API

**Project Directory:** `~/neo4j-api/`
**Version:** 1.0.0
**Date:** 2025-11-03

## Project Overview

Build a minimal, test-driven FastAPI application that mimics Linkurious Enterprise's REST API endpoints, providing read-only access to Neo4j 5.x multi-database instance with simple API key authentication.

---

## Development Principles

### 1. **Specification-Driven Development**
- Write OpenAPI spec FIRST before any code
- Use spec as contract between frontend and backend
- Validate implementation against spec

### 2. **Test-Driven Development (TDD)**
- Write tests BEFORE implementation
- Red → Green → Refactor cycle
- Minimum 80% code coverage

### 3. **GitHub Workflow**
- ✅ **Never work directly on `main` branch**
- ✅ **All changes via Pull Requests**
- ✅ **Branch naming:** `feature/endpoint-name`, `fix/bug-description`, `test/component-name`
- ✅ **PR requires:** Tests passing, code review approval
- ✅ **CI/CD:** GitHub Actions for automated testing

---

## Project Structure

```
~/neo4j-api/
├── IMPLEMENTATION_PLAN.md      # This file
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── .env.example                # Example environment variables
├── .env                        # Actual environment (git-ignored)
│
├── openapi.yaml                # OpenAPI 3.1 specification (SPEC-FIRST)
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── dependencies.py         # FastAPI dependencies (auth, etc.)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── search.py           # Search endpoints
│   │   ├── query.py            # Query execution endpoints
│   │   ├── nodes.py            # Node operations
│   │   ├── schema.py           # Schema endpoints
│   │   └── health.py           # Health check
│   └── utils/
│       ├── __init__.py
│       ├── neo4j_client.py     # Neo4j connection wrapper
│       └── validators.py       # Query validation
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_health.py          # Health endpoint tests
│   ├── test_search.py          # Search endpoint tests
│   ├── test_query.py           # Query execution tests
│   ├── test_nodes.py           # Node operation tests
│   ├── test_schema.py          # Schema endpoint tests
│   ├── test_auth.py            # Authentication tests
│   └── test_validators.py     # Validator tests
│
├── scripts/
│   ├── setup_dev.sh            # Development setup script
│   └── run_tests.sh            # Test runner script
│
├── deployment/
│   ├── Caddyfile               # Caddy reverse proxy config
│   ├── neo4j-api.service       # systemd service file
│   └── docker-compose.yml      # Optional Docker deployment
│
└── .github/
    └── workflows/
        ├── test.yml            # CI: Run tests on PR
        └── deploy.yml          # CD: Deploy on merge to main
```

---

## Phase 1: Specification & Setup (Day 1, ~2 hours)

### Tasks:

1. **Create GitHub repository**
   ```bash
   cd ~/neo4j-api
   git init
   git checkout -b setup/initial
   ```

2. **Write OpenAPI Specification** (`openapi.yaml`)
   - Document ALL endpoints before coding
   - Define request/response schemas
   - Define security schemes (API Key)
   - Tool: Use Swagger Editor to validate

3. **Create project structure**
   - All directories and `__init__.py` files
   - `.gitignore` for Python
   - `README.md` with project overview

4. **Setup dependencies**

   **`requirements.txt`:**
   ```
   fastapi==0.115.0
   uvicorn[standard]==0.30.0
   neo4j==5.25.0
   python-dotenv==1.0.0
   pydantic==2.9.0
   pydantic-settings==2.5.0
   ```

   **`requirements-dev.txt`:**
   ```
   pytest==8.3.0
   pytest-asyncio==0.24.0
   pytest-cov==5.0.0
   httpx==0.27.0           # For testing FastAPI
   pytest-mock==3.14.0
   black==24.8.0           # Code formatter
   ruff==0.6.0             # Linter
   mypy==1.11.0            # Type checker
   ```

5. **Create `.env.example`**
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password_here
   API_KEY=your-secret-api-key-here
   ```

6. **Setup GitHub Actions** (`.github/workflows/test.yml`)
   ```yaml
   name: Test Suite

   on:
     pull_request:
       branches: [ main ]
     push:
       branches: [ main ]

   jobs:
     test:
       runs-on: ubuntu-latest

       steps:
       - uses: actions/checkout@v4

       - name: Set up Python
         uses: actions/setup-python@v5
         with:
           python-version: '3.11'

       - name: Install dependencies
         run: |
           pip install -r requirements.txt
           pip install -r requirements-dev.txt

       - name: Run linter
         run: ruff check .

       - name: Run type checker
         run: mypy app/

       - name: Run tests with coverage
         run: pytest --cov=app --cov-report=xml --cov-report=term

       - name: Check coverage threshold
         run: |
           coverage report --fail-under=80
   ```

7. **First PR:** `setup/initial` → `main`

---

## Phase 2: TDD - Health & Database Endpoints (Day 1-2, ~3 hours)

### Branch: `feature/health-endpoints`

### Step 1: Write Tests FIRST

**`tests/conftest.py`:**
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver"""
    with patch('app.utils.neo4j_client.GraphDatabase.driver') as mock:
        driver = Mock()
        mock.return_value = driver
        yield driver

@pytest.fixture
def api_key():
    """Valid API key for testing"""
    return "test-api-key"
```

**`tests/test_health.py`:**
```python
import pytest
from fastapi import status

def test_health_check_success(client, mock_neo4j_driver):
    """Test health check returns 200 when Neo4j is connected"""
    mock_neo4j_driver.verify_connectivity.return_value = True

    response = client.get("/api/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"
    assert response.json()["neo4j"] == "connected"

def test_health_check_neo4j_down(client, mock_neo4j_driver):
    """Test health check returns 503 when Neo4j is down"""
    mock_neo4j_driver.verify_connectivity.side_effect = Exception("Connection failed")

    response = client.get("/api/health")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["status"] == "unhealthy"

def test_list_databases_success(client, mock_neo4j_driver):
    """Test listing databases returns database list"""
    mock_neo4j_driver.execute_query.return_value = (
        [{"name": "neo4j", "default": True}, {"name": "system", "default": False}],
        None,
        None
    )

    response = client.get("/api/databases")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["databases"]) == 2
```

### Step 2: Implement Code (Red → Green)

**`app/main.py`:**
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import health
from app.utils.neo4j_client import neo4j_driver

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    neo4j_driver.connect()
    yield
    # Shutdown
    neo4j_driver.close()

app = FastAPI(
    title="Neo4j Multi-Database REST API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health.router, prefix="/api", tags=["health"])
```

**`app/routers/health.py`:**
```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.neo4j_client import neo4j_driver
from neo4j import RoutingControl

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        neo4j_driver.verify_connectivity()
        return {"status": "healthy", "neo4j": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@router.get("/databases")
async def list_databases():
    try:
        records, _, _ = neo4j_driver.execute_query(
            "SHOW DATABASES",
            routing_=RoutingControl.READ
        )
        databases = [
            {"name": r["name"], "default": r.get("default", False)}
            for r in records
        ]
        return {"databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 3: Run Tests
```bash
pytest tests/test_health.py -v
```

### Step 4: Refactor (if needed)

### Step 5: Create PR
```bash
git checkout -b feature/health-endpoints
git add .
git commit -m "feat: add health check and database list endpoints with tests"
git push origin feature/health-endpoints
```

**PR Title:** `feat: Health check and database listing endpoints`
**PR Description:**
- ✅ Tests written first (TDD)
- ✅ Health endpoint with Neo4j connectivity check
- ✅ Database listing endpoint
- ✅ 100% test coverage for health module
- ✅ Matches OpenAPI spec

---

## Phase 3: TDD - Authentication (Day 2, ~2 hours)

### Branch: `feature/api-key-auth`

### Step 1: Write Tests FIRST

**`tests/test_auth.py`:**
```python
import pytest
from fastapi import status

def test_missing_api_key_returns_403(client):
    """Test that missing API key returns 403"""
    response = client.get("/api/neo4j/graph/nodes/count")
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_invalid_api_key_returns_403(client):
    """Test that invalid API key returns 403"""
    response = client.get(
        "/api/neo4j/graph/nodes/count",
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_valid_api_key_allows_access(client, mock_neo4j_driver, api_key):
    """Test that valid API key grants access"""
    mock_neo4j_driver.execute_query.return_value = ([{"count": 100}], None, None)

    response = client.get(
        "/api/neo4j/graph/nodes/count",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == status.HTTP_200_OK

def test_health_endpoint_does_not_require_auth(client):
    """Test that health endpoint is public"""
    response = client.get("/api/health")
    # Should not return 403, even without API key
    assert response.status_code != status.HTTP_403_FORBIDDEN
```

### Step 2: Implement

**`app/dependencies.py`:**
```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key
```

### Step 3: Run Tests → Green

### Step 4: Create PR

---

## Phase 4: TDD - Search Endpoints (Day 2-3, ~3 hours)

### Branch: `feature/search-endpoints`

### Tests First

**`tests/test_search.py`:**
```python
def test_search_nodes_returns_results(client, mock_neo4j_driver, api_key):
    """Test search returns node results"""
    mock_neo4j_driver.execute_query.return_value = (
        [{"n": MockNode(id=1, labels=["Person"], props={"name": "Alice"})}],
        None,
        None
    )

    response = client.get(
        "/api/testdb/search/node/full?q=Alice&fuzziness=0.7",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "node"
    assert len(data["results"]) == 1
    assert data["results"][0]["properties"]["name"] == "Alice"

def test_search_with_invalid_database_returns_404(client, api_key):
    """Test search on non-existent database returns 404"""
    response = client.get(
        "/api/invalid_db/search/node/full?q=test",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 404

def test_search_requires_query_parameter(client, api_key):
    """Test search without q parameter returns 422"""
    response = client.get(
        "/api/testdb/search/node/full",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 422  # Validation error
```

### Implement → Test → Refactor → PR

---

## Phase 5: TDD - Query Execution (Day 3-4, ~4 hours)

### Branch: `feature/query-execution`

### Tests First

**`tests/test_query.py`:**
```python
def test_execute_read_query_success(client, mock_neo4j_driver, api_key):
    """Test executing valid read query"""
    # ... test implementation

def test_execute_write_query_blocked(client, api_key):
    """Test that CREATE/DELETE queries are blocked"""
    response = client.post(
        "/api/testdb/graph/query",
        headers={"X-API-Key": api_key},
        json={"query": "CREATE (n:Person {name: 'Bad'}) RETURN n"}
    )
    assert response.status_code == 403
    assert "read-only" in response.json()["detail"].lower()

def test_query_with_parameters(client, mock_neo4j_driver, api_key):
    """Test parameterized queries"""
    # ... test implementation

def test_query_timeout_handling(client, mock_neo4j_driver, api_key):
    """Test query timeout returns appropriate error"""
    # ... test implementation
```

### Validator Tests

**`tests/test_validators.py`:**
```python
from app.utils.validators import is_read_only_query

def test_match_query_is_read_only():
    assert is_read_only_query("MATCH (n) RETURN n") is True

def test_create_query_is_not_read_only():
    assert is_read_only_query("CREATE (n:Person) RETURN n") is False

def test_delete_query_is_not_read_only():
    assert is_read_only_query("MATCH (n) DELETE n") is False

def test_merge_query_is_not_read_only():
    assert is_read_only_query("MERGE (n:Person {id: 1})") is False

def test_call_db_procedures_are_read_only():
    assert is_read_only_query("CALL db.labels()") is True

def test_show_commands_are_read_only():
    assert is_read_only_query("SHOW DATABASES") is True
```

### Implement → Test → Refactor → PR

---

## Phase 6: TDD - Node Operations (Day 4, ~3 hours)

### Branch: `feature/node-operations`

### Tests covering:
- Get node by ID
- Expand node (get neighbors)
- Node count
- Invalid node IDs
- Non-existent nodes

### Implement → Test → Refactor → PR

---

## Phase 7: TDD - Schema Endpoints (Day 4, ~2 hours)

### Branch: `feature/schema-endpoints`

### Tests covering:
- Get node labels
- Get relationship types
- Empty schema handling

### Implement → Test → Refactor → PR

---

## Phase 8: Integration & Deployment (Day 5, ~4 hours)

### Branch: `deployment/caddy-setup`

### Caddy Configuration

**`deployment/Caddyfile`:**
```
{
    # Global options
    admin off
}

# HTTP server (or use your NAT-IP/domain)
:80 {
    # API endpoints
    handle /api/* {
        reverse_proxy localhost:8000 {
            # Health checks
            health_uri /api/health
            health_interval 10s
            health_timeout 5s

            # Timeouts for long-running queries
            transport http {
                read_timeout 5m
                write_timeout 5m
            }
        }
    }

    # Default response
    respond "Neo4j API - Use /api/docs for documentation" 200

    # Logging
    log {
        output file /var/log/caddy/neo4j-api.log
        format json
    }
}

# HTTPS (optional - uncomment when ready)
# your-domain.com {
#     reverse_proxy localhost:8000
#     tls your-email@example.com
# }
```

### Systemd Service

**`deployment/neo4j-api.service`:**
```ini
[Unit]
Description=Neo4j Multi-Database REST API
After=network.target
Wants=caddy.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/neo4j-api
Environment="PATH=/home/YOUR_USERNAME/neo4j-api/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/YOUR_USERNAME/neo4j-api/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Deployment Script

**`scripts/deploy.sh`:**
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Neo4j API..."

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Restart service
sudo systemctl restart neo4j-api

# Check status
sudo systemctl status neo4j-api

# Test health endpoint
sleep 2
curl -s http://localhost/api/health | jq

echo "✅ Deployment complete!"
```

### Installation Steps

**`scripts/setup_production.sh`:**
```bash
#!/bin/bash
set -e

echo "🔧 Setting up Neo4j API production environment..."

# 1. Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv debian-keyring debian-archive-keyring apt-transport-https curl jq

# 2. Install Caddy
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# 3. Create virtual environment
cd ~/neo4j-api
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env with your Neo4j credentials and API key"
    read -p "Press enter after updating .env..."
fi

# 6. Run tests
pytest tests/ -v

# 7. Setup systemd service
sudo cp deployment/neo4j-api.service /etc/systemd/system/
sudo sed -i "s/YOUR_USERNAME/$USER/g" /etc/systemd/system/neo4j-api.service
sudo systemctl daemon-reload
sudo systemctl enable neo4j-api
sudo systemctl start neo4j-api

# 8. Setup Caddy
sudo cp deployment/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy

# 9. Create log directory
sudo mkdir -p /var/log/caddy
sudo chown caddy:caddy /var/log/caddy

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit .env with your credentials: nano ~/neo4j-api/.env"
echo "  2. Test the API: curl http://localhost/api/health"
echo "  3. View logs: sudo journalctl -u neo4j-api -f"
echo "  4. View API docs: http://YOUR_IP/api/docs"
```

---

## GitHub Workflow Summary

### Branch Strategy

```
main (protected)
  ↑
  ├── feature/health-endpoints
  ├── feature/api-key-auth
  ├── feature/search-endpoints
  ├── feature/query-execution
  ├── feature/node-operations
  ├── feature/schema-endpoints
  └── deployment/caddy-setup
```

### PR Process

1. **Create branch from main:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature
   ```

2. **Write tests first (TDD):**
   ```bash
   # Write failing tests
   pytest tests/test_your_feature.py  # RED
   ```

3. **Implement feature:**
   ```bash
   # Write minimal code to pass tests
   pytest tests/test_your_feature.py  # GREEN
   ```

4. **Refactor:**
   ```bash
   # Improve code quality
   black app/
   ruff check app/
   mypy app/
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: add your feature with tests"
   git push origin feature/your-feature
   ```

6. **Create PR on GitHub:**
   - Title: `feat: descriptive title`
   - Description: What, why, testing notes
   - Request review
   - Wait for CI to pass

7. **After approval, squash and merge to main**

8. **Delete branch:**
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/your-feature
   ```

### Protected Main Branch Rules

Set on GitHub:
- ✅ Require pull request before merging
- ✅ Require status checks to pass (CI tests)
- ✅ Require branches to be up to date
- ✅ Require linear history (squash merges)
- ❌ No direct pushes to main
- ✅ Require code review approval (at least 1)

---

## Testing Strategy

### Test Pyramid

```
        /\
       /  \    E2E Tests (5%)
      /    \   - Full API integration tests
     /------\
    /        \ Integration Tests (15%)
   /          \ - Database integration
  /            \ - Router integration
 /--------------\
/                \ Unit Tests (80%)
                  - Pure functions
                  - Validators
                  - Models
```

### Coverage Requirements

- **Minimum:** 80% overall
- **Routers:** 90%+
- **Validators:** 100%
- **Utils:** 85%+

### Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_health.py -v

# Run tests matching pattern
pytest -k "test_search" -v

# Run with detailed output
pytest -vv --tb=short

# Watch mode (requires pytest-watch)
ptw -- --testmon
```

---

## Timeline

| Phase | Duration | Branch | Deliverable |
|-------|----------|--------|-------------|
| 1. Spec & Setup | 2 hours | `setup/initial` | OpenAPI spec, project structure, CI/CD |
| 2. Health Endpoints (TDD) | 3 hours | `feature/health-endpoints` | Health check, database list + tests |
| 3. Authentication (TDD) | 2 hours | `feature/api-key-auth` | API key auth + tests |
| 4. Search (TDD) | 3 hours | `feature/search-endpoints` | Node search + tests |
| 5. Query Execution (TDD) | 4 hours | `feature/query-execution` | Cypher queries + tests |
| 6. Node Operations (TDD) | 3 hours | `feature/node-operations` | Node CRUD + tests |
| 7. Schema (TDD) | 2 hours | `feature/schema-endpoints` | Schema APIs + tests |
| 8. Deployment | 4 hours | `deployment/caddy-setup` | Caddy + systemd setup |
| **Total** | **23 hours** | **~3 days** | **Production-ready API** |

---

## Success Criteria

### Code Quality
- ✅ 80%+ test coverage
- ✅ All tests passing
- ✅ No linting errors (ruff)
- ✅ No type errors (mypy)
- ✅ Black formatted

### Functionality
- ✅ All Linkurious endpoints implemented
- ✅ Multi-database routing works
- ✅ Read-only enforcement
- ✅ API key authentication
- ✅ OpenAPI docs accessible

### Deployment
- ✅ Runs as systemd service
- ✅ Caddy reverse proxy configured
- ✅ Accessible from NAT-IP
- ✅ Auto-restart on failure
- ✅ Logs available

### Process
- ✅ No commits to main
- ✅ All PRs reviewed
- ✅ All PRs have passing tests
- ✅ Spec-driven development followed
- ✅ TDD cycle followed

---

## Key Commands Reference

```bash
# Development
source venv/bin/activate
uvicorn app.main:app --reload

# Testing
pytest -v --cov=app
pytest -k "test_name" -v

# Code quality
black app/ tests/
ruff check app/ tests/
mypy app/

# Git workflow
git checkout -b feature/name
git commit -m "type: message"
git push origin feature/name

# Deployment
sudo systemctl restart neo4j-api
sudo systemctl status neo4j-api
sudo journalctl -u neo4j-api -f

# Caddy
sudo systemctl reload caddy
caddy validate --config /etc/caddy/Caddyfile
```

---

## Notes

- This plan follows TDD principles: **Write tests first, then implement**
- All work is done in feature branches, never directly on `main`
- OpenAPI specification is written before any code
- Caddy is used as the reverse proxy (not nginx)
- Minimum 80% test coverage required
- GitHub Actions will enforce tests passing before merging
