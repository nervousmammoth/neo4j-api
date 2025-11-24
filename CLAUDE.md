# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A **Linkurious-compatible REST API** for Neo4j Enterprise multi-database instances built with FastAPI. The project follows **Specification-Driven Development** and **Test-Driven Development (TDD)** using **pytest** for unit and integration tests with 100% coverage enforcement.

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
├── app/                    # FastAPI application
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

# Setup Git hooks (REQUIRED for development)
./scripts/setup_hooks.sh
```

### Git Hooks Setup

**IMPORTANT:** This project enforces code quality and 100% test coverage through Git hooks.

**Installation:**
```bash
# One-time setup (run after cloning the repository)
./scripts/setup_hooks.sh
```

**What gets installed:**

1. **Pre-commit hooks** (runs on `git commit`, ~5-10 seconds):
   - **Black** - Auto-formats Python code
   - **Ruff** - Lints and auto-fixes code issues
   - **mypy** - Type checking with strict mode
   - **Bandit** - Security vulnerability scanning
   - **File checks** - Trailing whitespace, file endings, YAML/TOML/JSON syntax
   - **Conventional commits** - Enforces commit message format (feat:, fix:, test:, etc.)

2. **Pre-push hook** (runs on `git push`, ~30-60 seconds):
   - **Unit tests** - All pytest tests with 100% coverage requirement

**Manual hook execution:**
```bash
# Run all pre-commit checks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run ruff --all-files
pre-commit run mypy --all-files

# Update hook versions
pre-commit autoupdate
```

**Bypassing hooks (NOT RECOMMENDED):**
```bash
# Skip pre-commit checks
git commit --no-verify -m "message"

# Skip pre-push checks
git push --no-verify
```

**Note:** Until the `app/` directory is implemented, hooks will pass with warnings. Once implementation begins, 100% test coverage becomes mandatory.

**Coverage enforcement:**
- **Threshold:** 100% for branches, functions, lines, and statements
- **Exclusions:** tests/, __init__.py files
- **Reports:** Terminal output + HTML (htmlcov/index.html) + XML (coverage.xml)
- **Failure:** Push is blocked if coverage < 100%

**Configuration files:**
- `.pre-commit-config.yaml` - Pre-commit hook definitions
- `pyproject.toml` - Coverage thresholds and tool settings
- `scripts/pre-push.template` - Custom pre-push hook script

### Running Tests

**Complete Test Suite:**
```bash
./scripts/run_all_tests.sh  # Unit tests + code quality
```

**Unit Tests:**
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
black app/ tests/                       # Format code
ruff check app/ tests/                  # Lint
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

## Issue-Based Development Workflow

This project uses a **ticket-driven workflow** where all development work is organized into small, manageable issues (1-3 hours each). Each issue has its own branch, follows TDD principles, and moves through a defined lifecycle.

### Directory Structure

```
issues/
├── README.md                    # Workflow overview
├── templates/
│   └── ticket-template.md       # Template for new issues
├── [XX-ticket-name.md]          # Active issues
└── completed/
    └── [XX-ticket-name.md]      # Completed issues
```

### Issue Lifecycle

```
📝 Created → 🚧 In Progress → 🔍 PR Review → ✅ Merged → 📦 Completed (moved to /completed)
```

### Issue Numbering Convention

Issues are numbered sequentially with zero-padded two-digit numbers:
- **Phase 0 (Foundation):** `00-03` - Project setup, README, .env.example
- **Phase 1 (Core Infrastructure):** `04-09` - Config, Neo4j client, validators, auth
- **Phase 2 (Health Endpoints):** `10-12` - Health check, databases list
- **Phase 3 (Query Execution):** `13-16` - Cypher query endpoint with validation
- **Phase 4 (Search Endpoints):** `17-20` - Node and edge search
- **Phase 5 (Node Operations):** `21-25` - Get, expand, count operations
- **Phase 6 (Schema Endpoints):** `26-29` - Schema discovery
- **Phase 7 (Integration):** `32` - Coverage verification
- **Phase 8 (Deployment):** `33-35` - Production deployment configs

### Branch Naming Convention

```bash
# Format: issue/XX-short-description
issue/00-create-readme
issue/05-neo4j-client
issue/14-query-endpoint-basic
```

### Commit Message Format

Follow conventional commits with issue reference:

```bash
# Format: type(issue-XX): description
git commit -m "feat(issue-00): add project README with quickstart"
git commit -m "test(issue-05): add unit tests for Neo4j client"
git commit -m "fix(issue-14): correct query response format"
```

**Commit types:**
- `feat:` - New feature
- `test:` - Adding/updating tests
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `chore:` - Maintenance

### Working on an Issue

#### 1. Start Issue
```bash
# Check current issues
ls issues/*.md

# Create branch
git checkout main
git pull origin main
git checkout -b issue/XX-ticket-name

# Open ticket file to review
cat issues/XX-ticket-name.md
```

#### 2. Follow TDD Cycle (Red → Green → Refactor)

**RED - Write failing tests:**
```bash
# Create test file
touch tests/test_your_module.py

# Write tests first
# Run: pytest tests/test_your_module.py -v
# Expect: FAIL ❌
```

**GREEN - Implement minimum code:**
```bash
# Create implementation file
touch app/your_module.py

# Implement code to pass tests
# Run: pytest tests/test_your_module.py -v
# Expect: PASS ✅
```

**REFACTOR - Improve code quality:**
```bash
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# Run: pytest tests/test_your_module.py -v
# Expect: Still PASS ✅
```

#### 3. Verify Quality Gates

```bash
# Run unit tests with coverage
pytest --cov=app --cov-fail-under=100 --cov-report=term-missing

# Run all pre-commit checks
pre-commit run --all-files
```

#### 4. Commit and Push

```bash
# Stage changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "feat(issue-XX): implement feature"

# Push
git push origin issue/XX-ticket-name
```

#### 5. Create Pull Request

```bash
gh pr create \
  --title "feat: [Issue title]" \
  --body "$(cat <<'EOF'
## Summary
- [What was implemented]

## Changes
- [File changes]

## Testing
- [x] Unit tests pass (pytest)
- [x] 100% coverage achieved
- [x] Pre-commit hooks pass

## Closes
Closes #XX

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

#### 6. After Merge

```bash
# Move ticket to completed
mv issues/XX-ticket-name.md issues/completed/

# Update local main
git checkout main
git pull origin main

# Verify merge
git log -1

# Ready for next issue
ls issues/*.md
```

### Issue Template Usage

To create a new issue:

```bash
# Copy template
cp issues/templates/ticket-template.md issues/XX-new-feature.md

# Edit with issue details
nano issues/XX-new-feature.md
```

The template includes:
- Status tracking
- Related specifications
- Dependencies
- TDD workflow checklist (Red → Green → Refactor)
- Acceptance criteria
- Implementation notes
- Git workflow commands
- Verification commands

### Finding Available Issues

```bash
# List all active issues
ls -1 issues/*.md

# View issue details
cat issues/XX-ticket-name.md

# Check completed issues
ls -1 issues/completed/

# See issue status (look for Status section in file)
head -n 10 issues/XX-ticket-name.md
```

### Issue Dependencies

Some issues depend on others. Check the **Dependencies** section in each ticket:

```markdown
## Dependencies
- [ ] Issue #04 - Config module must be implemented first
- [ ] Issue #05 - Neo4j client must be implemented first
```

**Work order:**
1. Complete dependency issues first
2. Check dependencies are merged to main
3. Start dependent issue from updated main branch

### Quality Standards Per Issue

Every issue must meet these standards before PR:

✅ **Code Quality:**
- [ ] Black formatting applied
- [ ] Ruff linting passed (no warnings)
- [ ] mypy type checking passed (no errors)
- [ ] Bandit security scan passed

✅ **Testing:**
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage for new code
- [ ] No test regression (all existing tests pass)

✅ **Documentation:**
- [ ] Docstrings present (Google style)
- [ ] Type hints on all functions
- [ ] Comments for complex logic

✅ **Git Hygiene:**
- [ ] Commits follow conventional commit format
- [ ] Commit messages are clear and descriptive
- [ ] Pre-commit hooks pass
- [ ] Branch is up-to-date with main

### Troubleshooting

**Issue: Pre-commit hooks failing**
```bash
# Run specific check
pre-commit run black --all-files
pre-commit run ruff --all-files
pre-commit run mypy --all-files

# Update hooks
pre-commit autoupdate
```

**Issue: Coverage below 100%**
```bash
# Generate detailed report
pytest --cov=app --cov-report=html

# Open report
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # macOS

# Check which lines are missing coverage
pytest --cov=app --cov-report=term-missing
```

**Issue: Merge conflicts**
```bash
# Update branch with latest main
git checkout main
git pull origin main
git checkout issue/XX-ticket-name
git merge main

# Resolve conflicts
# ... edit files ...
git add .
git commit -m "chore(issue-XX): resolve merge conflicts"
```

### Tips for Efficient Issue Work

1. **Read the spec first** - Always check `specs/` before coding
2. **Small commits** - Commit after each TDD cycle (Red, Green, Refactor)
3. **Use fixtures** - Reuse test fixtures from `tests/conftest.py`
4. **Mock Neo4j** - Always mock `GraphDatabase.driver` in unit tests
5. **Verify locally** - Run all checks before pushing
6. **Update ticket** - Check off items in ticket as you complete them

### Progress Tracking

Track overall project progress:

```bash
# Count total issues
ls -1 issues/*.md | wc -l

# Count completed issues
ls -1 issues/completed/*.md | wc -l

# Show percentage complete
echo "scale=2; $(ls -1 issues/completed/*.md 2>/dev/null | wc -l) / 35 * 100" | bc

# View next issue to work on (lowest number)
ls -1 issues/*.md | head -1
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

3. **Write Unit Tests First (RED)**
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

**STRICT ENFORCEMENT:** This project requires **100% test coverage** for all metrics, enforced by pre-push Git hooks.

- **Branches:** 100% (every conditional path must be tested)
- **Functions:** 100% (every function must be called in tests)
- **Lines:** 100% (every line of code must be executed)
- **Statements:** 100% (every statement must be tested)

**Exclusions:**
- `tests/` directory
- `__init__.py` files (empty module initializers)
- `conftest.py` (pytest configuration)
- Abstract methods and NotImplementedError cases

**Check coverage:**
```bash
# Run tests with coverage report
pytest --cov=app --cov-report=term-missing --cov-report=html

# View detailed HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Enforce 100% threshold (fails if below 100%)
pytest --cov=app --cov-fail-under=100
```

**Coverage configuration:** See `pyproject.toml` for complete settings.

## Common Pitfalls

1. **Don't mock FastAPI dependencies in unit tests** - Use `TestClient` with dependency overrides
2. **Always validate against specs** - Implementation must match `specs/endpoints-*.md` exactly
3. **Mock Neo4j driver, not FastAPI** - Use `@patch('app.utils.neo4j_client.GraphDatabase.driver')`
4. **Read-only validation is critical** - Never skip query validation tests
5. **Public endpoints** - `/api/health` and `/api/databases` must NOT require authentication
6. **Linkurious format** - Response structure must match Linkurious API (see `specs/data-models.md`)

## Project Status

**Current state:** Specifications complete. FastAPI implementation in progress.

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
- **`IMPLEMENTATION_PLAN.md`** - Detailed TDD implementation plan with examples
- **`issues/README.md`** - Issue-based workflow and ticket tracking
- **`README.md`** - Project overview and quick start
