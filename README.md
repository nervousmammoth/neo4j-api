# Neo4j API - Linkurious-Compatible REST API

A read-only REST API for Neo4j Enterprise multi-database instances, providing Linkurious-compatible endpoints for graph visualization and exploration.

## Overview

This project implements a FastAPI-based REST API that serves as a bridge between Linkurious Enterprise clients and Neo4j Enterprise databases. It provides a read-only interface with comprehensive security validation, multi-database support, and production-ready deployment with Caddy reverse proxy.

**Key Constraint:** All write operations (CREATE, DELETE, MERGE, SET, REMOVE, DROP) are blocked by query validation to ensure data safety.

## Features

- **Read-Only API** - Write operations blocked at query validation layer
- **Linkurious-Compatible** - Response formats match Linkurious Enterprise API
- **Multi-Database Support** - Route to different Neo4j databases via path: `/api/{database}/...`
- **API Key Authentication** - Secure access with X-API-Key header validation
- **Comprehensive Testing** - pytest for unit and integration tests with 100% coverage
- **100% Test Coverage** - Enforced via Git hooks
- **Specification-Driven** - All endpoints defined in `specs/` before implementation
- **Production Ready** - Caddy reverse proxy with automatic HTTPS

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

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Neo4j Enterprise 5.x with multi-database support
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/nervousmammoth/neo4j-api.git
cd neo4j-api

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# Or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your Neo4j credentials and API key

# Setup Git hooks (required for development)
./scripts/setup_hooks.sh
```

### Configuration

Create a `.env` file with the following variables:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# API Configuration
API_KEY=your_secure_api_key
HOST=0.0.0.0
PORT=8000

# Environment
ENVIRONMENT=development
```

### Running the API

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once the API is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### Example Request

```bash
# Health check (no authentication required)
curl http://localhost:8000/api/health

# List available databases
curl http://localhost:8000/api/databases

# Search nodes (requires API key)
curl -H "X-API-Key: your_secure_api_key" \
  "http://localhost:8000/api/neo4j/graph/search?query=Person"

# Execute Cypher query (read-only)
curl -X POST \
  -H "X-API-Key: your_secure_api_key" \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (n:Person) RETURN n LIMIT 10"}' \
  http://localhost:8000/api/neo4j/graph/query
```

## Development

### Project Structure

```
neo4j-api/
├── specs/                  # API specifications (source of truth)
├── app/                    # FastAPI application
│   ├── main.py             # FastAPI app with lifespan
│   ├── config.py           # Settings via pydantic-settings
│   ├── dependencies.py     # API key auth dependency
│   ├── routers/            # Endpoint routers
│   └── utils/              # Neo4j client & validators
├── tests/                  # Unit tests (pytest)
└── scripts/                # Development & deployment scripts
```

### Development Workflow

This project follows **Specification-Driven Development** and **Test-Driven Development (TDD)**:

1. Read specification in `specs/endpoints-*.md`
2. Write failing unit tests (RED)
3. Implement minimal code (GREEN)
4. Refactor and improve (REFACTOR)
5. Verify 100% test coverage

For detailed workflow, see [CLAUDE.md](CLAUDE.md).

### Git Hooks

This project enforces code quality through Git hooks:

**Pre-commit** (runs on every commit):
- Black - Code formatting
- Ruff - Linting
- mypy - Type checking
- Bandit - Security scanning
- Conventional commits validation

**Pre-push** (runs on every push):
- pytest - Unit tests with 100% coverage (when app/ exists)

Setup hooks with: `./scripts/setup_hooks.sh`

### Running Tests

```bash
# Run all tests (unit + quality checks)
./scripts/run_all_tests.sh

# Unit tests only
pytest
pytest --cov=app --cov-report=html  # With coverage report

# Code quality checks
black app/ tests/                       # Format code
ruff check app/ tests/                  # Lint
mypy app/                               # Type check
bandit -r app/                          # Security scan
```

### Testing Strategy

**Unit and Integration Testing with pytest:**

- Test individual components and complete workflows
- Coverage requirement: 100% (branches, functions, lines, statements)
- Fixtures in `tests/conftest.py`
- Mock Neo4j driver for all tests
- Markers: @unit, @integration, @smoke

### Code Quality Standards

All code must pass:
- **Black** - PEP 8 formatting
- **Ruff** - Linting (no warnings)
- **mypy** - Type checking (strict mode)
- **Bandit** - Security scanning (no issues)
- **100% test coverage** - All branches, functions, lines, statements

## API Endpoints

### Public Endpoints (No Authentication)

- `GET /api/health` - Health check
- `GET /api/databases` - List available databases
- `GET /api/docs` - Swagger UI documentation
- `GET /api/redoc` - ReDoc documentation

### Protected Endpoints (Require X-API-Key)

- `GET /api/{database}/graph/search` - Search nodes and edges
- `POST /api/{database}/graph/query` - Execute Cypher queries (read-only)
- `GET /api/{database}/graph/nodes/{id}` - Get node by ID
- `GET /api/{database}/graph/nodes/{id}/expand` - Expand node relationships
- `GET /api/{database}/graph/nodes/count` - Count nodes
- `GET /api/{database}/graph/schema` - Get database schema
- `GET /api/{database}/graph/schema/nodes` - Get node labels
- `GET /api/{database}/graph/schema/edges` - Get relationship types

See [specs/](specs/) for detailed endpoint specifications.

## Deployment

### Production Setup

```bash
# Run production setup script
./scripts/setup_production.sh

# Service management
sudo systemctl start neo4j-api
sudo systemctl stop neo4j-api
sudo systemctl restart neo4j-api
sudo systemctl status neo4j-api

# View logs
sudo journalctl -u neo4j-api -f
```

### Caddy Configuration

Caddy serves as a reverse proxy with automatic HTTPS:

```caddy
your-domain.com {
    reverse_proxy localhost:8000
    encode gzip
}
```

Reload Caddy: `sudo systemctl reload caddy`

## Documentation

- **[API Specifications](specs/)** - Complete endpoint specifications
- **[Development Guide](CLAUDE.md)** - Comprehensive development workflow
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - TDD implementation roadmap
- **[Issue Tracking](issues/)** - Ticket-driven development workflow

## Testing Standards

- **Coverage Requirement**: 100% for all metrics (branches, functions, lines, statements)
- **Test Framework**: pytest with comprehensive fixtures
- **Quality Gates**: Pre-commit and pre-push hooks enforce standards

## Contributing

1. Check available issues in `issues/` directory
2. Create feature branch: `git checkout -b issue/XX-description`
3. Follow TDD workflow (RED → GREEN → REFACTOR)
4. Ensure 100% test coverage
5. Run all quality checks: `./scripts/run_all_tests.sh`
6. Create pull request with conventional commit format

See [CLAUDE.md](CLAUDE.md) for detailed contribution guidelines.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- [Neo4j Python Driver](https://neo4j.com/developer/python/)
- [pytest](https://pytest.org/)
- [Caddy Web Server](https://caddyserver.com/)
