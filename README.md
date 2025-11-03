# Neo4j API

A **Linkurious-compatible REST API** for Neo4j Enterprise multi-database instances built with FastAPI. This API provides read-only access to Neo4j graph databases with comprehensive search, query, and schema discovery capabilities.

## Features

- **Multi-Database Support**: Route to different Neo4j databases via URL path parameter
- **Read-Only Security**: Query validation blocks all write operations (CREATE, DELETE, MERGE, SET, REMOVE)
- **Linkurious Compatibility**: Response formats match Linkurious Enterprise API
- **Comprehensive Testing**: 100% test coverage with pytest unit tests and behave BDD tests
- **API Key Authentication**: Secure X-API-Key header authentication
- **Health Checks**: Database connectivity and health monitoring endpoints

## Architecture

```
Client → Caddy (:80) → FastAPI (:8000) → Neo4j (:7687)
```

### Endpoints

- **Health & Status**
  - `GET /api/health` - API health check (no auth required)
  - `GET /api/databases` - List available databases (no auth required)

- **Graph Search**
  - `POST /api/{database}/graph/search/nodes` - Search nodes
  - `POST /api/{database}/graph/search/edges` - Search edges

- **Query Execution**
  - `POST /api/{database}/graph/query` - Execute Cypher queries (read-only)

- **Node Operations**
  - `GET /api/{database}/graph/nodes/{nodeId}` - Get node by ID
  - `POST /api/{database}/graph/nodes/{nodeId}/expand` - Get node relationships
  - `GET /api/{database}/graph/nodes/count` - Count total nodes

- **Schema Discovery**
  - `GET /api/{database}/graph/schema` - Get database schema
  - `GET /api/{database}/graph/schema/types` - Get node/edge types
  - `GET /api/{database}/graph/schema/properties` - Get property definitions

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: Neo4j 5.x (Enterprise Edition)
- **Testing**: pytest, behave (BDD), coverage
- **Code Quality**: Black, Ruff, mypy, Bandit
- **Server**: Uvicorn
- **Reverse Proxy**: Caddy

## Quick Start

### Prerequisites

- Python 3.11+
- Neo4j Enterprise 5.x
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/nervousmammoth/neo4j-api.git
cd neo4j-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# Or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials and API_KEY
```

### Configuration

Create a `.env` file with:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# API Configuration
API_KEY=your-secret-api-key
HOST=0.0.0.0
PORT=8000
```

### Running the API

**Development Mode:**
```bash
uvicorn app.main:app --reload
```

**Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Access API documentation:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Using the API

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Search Nodes (with authentication):**
```bash
curl -X POST http://localhost:8000/api/neo4j/graph/search/nodes \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "Person", "limit": 10}'
```

**Execute Cypher Query:**
```bash
curl -X POST http://localhost:8000/api/neo4j/graph/query \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (n:Person) RETURN n LIMIT 10"}'
```

## Development

### Setup Git Hooks

```bash
./scripts/setup_hooks.sh
```

This installs:
- **Pre-commit hooks**: Black, Ruff, mypy, Bandit (5-10s)
- **Pre-push hooks**: Unit tests with 100% coverage + BDD tests (1-2min)

### Running Tests

**All Tests:**
```bash
./scripts/run_all_tests.sh
```

**Unit Tests Only:**
```bash
pytest tests/ -v
pytest --cov=app --cov-report=html  # With coverage
```

**BDD Tests Only:**
```bash
./scripts/run_bdd_tests.sh              # All scenarios
./scripts/run_bdd_tests.sh --smoke      # Smoke tests only
behave features/ --tags=@smoke          # Specific tags
```

**Code Quality:**
```bash
black app/ tests/ features/             # Format
ruff check app/ tests/ features/        # Lint
mypy app/                               # Type check
```

### Test Coverage

This project enforces **100% test coverage** on:
- Branches
- Functions
- Lines
- Statements

Coverage report: `htmlcov/index.html`

## Project Structure

```
neo4j-api/
├── app/                    # FastAPI application
│   ├── main.py             # Application entry point
│   ├── config.py           # Settings management
│   ├── dependencies.py     # Auth dependencies
│   ├── routers/            # API endpoints
│   └── utils/              # Neo4j client, validators
├── tests/                  # Unit tests (pytest)
├── features/               # BDD tests (behave/Gherkin)
├── fixtures/               # Test fixtures
├── scripts/                # Automation scripts
└── .pre-commit-config.yaml # Git hooks configuration
```

## Security

### Read-Only Query Validation

All Cypher queries are validated to block write operations:

**Blocked keywords**: CREATE, DELETE, MERGE, SET, REMOVE, DROP
**Allowed patterns**: MATCH, RETURN, CALL db.*, SHOW, WITH, OPTIONAL MATCH

### Authentication

API key authentication via `X-API-Key` header is required for all endpoints except:
- `/api/health`
- `/api/databases`

## Deployment

### Using systemd (Linux)

```bash
# Setup production environment
./scripts/setup_production.sh

# Service management
sudo systemctl start neo4j-api
sudo systemctl stop neo4j-api
sudo systemctl restart neo4j-api
sudo systemctl status neo4j-api

# View logs
sudo journalctl -u neo4j-api -f
```

### Using Caddy (Reverse Proxy)

```bash
# Validate configuration
caddy validate --config /etc/caddy/Caddyfile

# Reload configuration
sudo systemctl reload caddy
```

## Development Workflow

This project follows **Specification-Driven Development** and **Test-Driven Development (TDD)**:

1. Write specifications
2. Write failing tests (RED)
3. Implement code to pass tests (GREEN)
4. Refactor while keeping tests green (REFACTOR)
5. Commit and push

See `CLAUDE.md` for detailed development guidelines.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes with conventional commits (`feat:`, `fix:`, `test:`, etc.)
4. Ensure 100% test coverage
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Built with FastAPI, Neo4j, and modern Python development practices.
