# Neo4j Multi-Database REST API

A lightweight, Linkurious-compatible REST API for Neo4j Enterprise multi-database instances. Built with FastAPI, following TDD principles and specification-driven development.

## 🎯 Project Goals

- **Replace Linkurious API:** Provide a minimal, open-source alternative to Linkurious Enterprise's REST API
- **Multi-Database Support:** Native routing to multiple Neo4j databases (Neo4j 4.0+ multi-tenancy)
- **Read-Only Safety:** Enforce read-only access to prevent accidental data modification
- **Developer-Friendly:** Auto-generated OpenAPI documentation, simple API key authentication
- **Production-Ready:** Systemd service, Caddy reverse proxy, comprehensive testing

## 📋 Features

- ✅ **Linkurious-Compatible Endpoints:** `/api/{database}/search/node/full`, `/api/{database}/graph/query`, etc.
- ✅ **Neo4j 5.x Native:** Uses latest Python driver with `execute_query` and multi-database support
- ✅ **API Key Authentication:** Simple `X-API-Key` header-based auth
- ✅ **Auto-Generated Docs:** Swagger UI at `/api/docs`, ReDoc at `/api/redoc`
- ✅ **Test-Driven:** 80%+ code coverage with pytest
- ✅ **Type-Safe:** Full type hints with mypy validation
- ✅ **Production Deployment:** Systemd + Caddy setup included

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Neo4j Enterprise 5.x with multi-database feature
- Git
- (Optional) Caddy for reverse proxy

### Local Development Setup

```bash
# Clone the repository
cd ~/neo4j-api
git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
cp .env.example .env
nano .env  # Edit with your Neo4j credentials

# Run tests
pytest -v

# Start development server
uvicorn app.main:app --reload

# Access the API
curl http://localhost:8000/api/health
# Open http://localhost:8000/api/docs for Swagger UI
```

## 📚 API Documentation

### Health & Metadata

```bash
# Health check (no auth required)
GET /api/health

# List available databases (no auth required)
GET /api/databases
```

### Search

```bash
# Search nodes (requires API key)
GET /api/{database}/search/node/full?q=searchterm&fuzziness=0.7
Headers: X-API-Key: your-api-key
```

### Query Execution

```bash
# Execute Cypher query (read-only)
POST /api/{database}/graph/query
Headers: X-API-Key: your-api-key
Body: {
  "query": "MATCH (n:Person) RETURN n LIMIT 10",
  "parameters": {}
}
```

### Node Operations

```bash
# Get node by ID
GET /api/{database}/graph/nodes/{node_id}
Headers: X-API-Key: your-api-key

# Expand node (get neighbors)
POST /api/{database}/graph/nodes/expand
Headers: X-API-Key: your-api-key
Body: {
  "ids": ["123", "456"]
}

# Node count
GET /api/{database}/graph/nodes/count
Headers: X-API-Key: your-api-key

# Edge count
GET /api/{database}/graph/edges/count
Headers: X-API-Key: your-api-key
```

### Schema

```bash
# Get node labels
GET /api/{database}/graph/schema/node/types
Headers: X-API-Key: your-api-key

# Get relationship types
GET /api/{database}/graph/schema/edge/types
Headers: X-API-Key: your-api-key
```

## 🧪 Testing

This project uses a **dual testing strategy**: **pytest** for unit tests and **behave** for BDD acceptance tests.

### Quick Start: Run All Tests

```bash
# Run everything: unit tests + BDD tests + code quality
./scripts/run_all_tests.sh
```

### Unit Tests (pytest)

Unit tests for individual functions, validators, and utilities:

```bash
# Run all unit tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_health.py -v

# Run tests matching pattern
pytest -k "test_search" -v

# Watch mode (auto-run on file changes)
ptw -- --testmon
```

### BDD Acceptance Tests (behave)

Behavior-Driven Development tests written in Gherkin that validate API behavior against specifications:

```bash
# Run all BDD tests
./scripts/run_bdd_tests.sh

# Run smoke tests only
./scripts/run_bdd_tests.sh --smoke

# Run tests by tag
./scripts/run_bdd_tests.sh --tag=auth
./scripts/run_bdd_tests.sh --tag=search
./scripts/run_bdd_tests.sh --tag=critical

# Run behave directly with custom options
behave features/ --tags=@smoke --format=pretty
behave features/ --tags=@health --no-capture
behave features/health.feature -v
```

### Available BDD Test Tags

- `@smoke` - Critical smoke tests (run first)
- `@critical` - High-priority tests
- `@health` - Health & metadata endpoints
- `@auth` - Authentication tests
- `@search` - Search functionality
- `@query` - Cypher query execution
- `@nodes` - Node operations
- `@schema` - Schema discovery
- `@database` - Multi-database tests
- `@error` - Error handling tests
- `@performance` - Performance tests
- `@integration` - Integration tests

### BDD Test Reports

After running BDD tests, view HTML reports:

```bash
# Open HTML report in browser
open reports/behave/index.html  # macOS
xdg-open reports/behave/index.html  # Linux

# View JSON results
cat reports/behave/results.json | jq
```

### Test Coverage Requirements

- **Overall:** 80% minimum
- **Routers:** 90%+
- **Validators:** 100%
- **Utils:** 85%+

### Writing BDD Tests

1. **Create a feature file** in `features/`:
   ```gherkin
   Feature: My New Feature
     Scenario: Test something
       Given the API is running
       When I send a GET request to "/api/endpoint"
       Then the response status code should be 200
   ```

2. **Implement step definitions** in `features/steps/`:
   ```python
   @when('I do something')
   def step_do_something(context):
       # Implementation
   ```

3. **Run your tests**:
   ```bash
   behave features/my_feature.feature
   ```

See `features/README.md` for detailed BDD testing documentation.

## 🔧 Development Workflow

### Branch Strategy

**Never commit directly to `main`!** All changes must go through Pull Requests.

```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Make changes following TDD:
# 1. Write tests first (RED)
# 2. Implement feature (GREEN)
# 3. Refactor (REFACTOR)

# Commit and push
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name

# Create PR on GitHub
# Wait for CI to pass
# Get code review approval
# Squash and merge to main
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `test:` Adding tests
- `refactor:` Code refactoring
- `docs:` Documentation changes
- `chore:` Maintenance tasks

### Code Quality

Before committing, ensure:

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type check
mypy app/

# Run tests
pytest --cov=app
```

## 🏭 Production Deployment

### Using Setup Script

```bash
cd ~/neo4j-api
chmod +x scripts/setup_production.sh
./scripts/setup_production.sh
```

This will:
1. Install system dependencies
2. Install Caddy reverse proxy
3. Setup Python virtual environment
4. Install Python dependencies
5. Configure systemd service
6. Setup Caddy reverse proxy
7. Start all services

### Manual Deployment

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) Phase 8 for detailed manual deployment steps.

### Deployment Architecture

```
Internet → Caddy (:80) → FastAPI (localhost:8000) → Neo4j (:7687)
```

### Service Management

```bash
# Start/stop API service
sudo systemctl start neo4j-api
sudo systemctl stop neo4j-api
sudo systemctl restart neo4j-api
sudo systemctl status neo4j-api

# View logs
sudo journalctl -u neo4j-api -f

# Reload Caddy config
sudo systemctl reload caddy

# Validate Caddy config
caddy validate --config /etc/caddy/Caddyfile
```

## 🔐 Security

### API Key Authentication

All endpoints except `/api/health` and `/api/databases` require an API key:

```bash
curl -H "X-API-Key: your-secret-key" http://your-server/api/{database}/graph/nodes/count
```

### Read-Only Enforcement

The API blocks write operations (CREATE, DELETE, MERGE, SET, REMOVE) to prevent accidental data modification. Only read queries (MATCH, RETURN, CALL db.*, SHOW) are allowed.

### Future Enhancements

- OAuth2/OIDC integration with Authentik (Phase 2)
- LDAP/SAML support (Phase 3)
- Fine-grained permissions per database
- Rate limiting
- Query result caching

## 📖 Documentation

- **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** - Full implementation plan with TDD approach
- **[OpenAPI Specification](./openapi.yaml)** - Complete API specification
- **[Swagger UI](http://localhost:8000/api/docs)** - Interactive API documentation
- **[ReDoc](http://localhost:8000/api/redoc)** - Alternative API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests first (TDD)
4. Implement the feature
5. Ensure tests pass (`pytest --cov=app`)
6. Ensure code quality (`black`, `ruff`, `mypy`)
7. Commit changes (`git commit -m 'feat: add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📊 Project Status

### Phase 1: Setup ⏳
- [ ] OpenAPI specification written
- [ ] Project structure created
- [ ] GitHub repository initialized
- [ ] CI/CD configured

### Phase 2-7: Features ⏳
- [ ] Health endpoints
- [ ] Authentication
- [ ] Search endpoints
- [ ] Query execution
- [ ] Node operations
- [ ] Schema endpoints

### Phase 8: Deployment ⏳
- [ ] Caddy configuration
- [ ] Systemd service
- [ ] Production deployment

## 🛠️ Tech Stack

- **Framework:** FastAPI 0.115.0
- **Database Driver:** neo4j 5.25.0
- **Testing:**
  - Unit Tests: pytest, pytest-cov, httpx
  - BDD Tests: behave, behave-html-formatter
- **Code Quality:** black, ruff, mypy
- **Reverse Proxy:** Caddy
- **Process Manager:** systemd

## 📝 License

[Add your license here]

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Linkurious Enterprise API documentation
- Neo4j Python Driver documentation
- FastAPI framework

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for detailed documentation
- Review [OpenAPI specification](./openapi.yaml) for API details

---

**Built with ❤️ following TDD and Specification-Driven Development principles**
