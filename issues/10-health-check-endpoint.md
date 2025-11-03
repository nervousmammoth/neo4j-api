# Issue 10: Implement Health Check Endpoint

## Status
⏳ **TODO**

**Estimated Time:** 2 hours
**Branch:** `issue/10-health-check-endpoint`
**Phase:** 2 - Health Endpoints

## Description
Implement `GET /api/health` endpoint in `app/routers/health.py` for health check and Neo4j connectivity status. This endpoint is public (no authentication required) and returns database connection status.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-health.md` - Section 1 (Health Check)
- [ ] **Spec file:** `specs/data-models.md` - Health response model
- [ ] **Spec file:** `specs/error-handling.md` - Health check errors

## Related BDD Tests
- [ ] **Feature file:** `features/health.feature`
- [ ] **Scenarios:** "Health endpoint returns 200", "Health check shows Neo4j status"
- [ ] **Tags:** `@health`, `@smoke`

## Dependencies
- [ ] Issue #04 - Config module
- [ ] Issue #05 - Neo4j client
- [ ] Issue #07 - Base models
- [ ] Issue #09 - FastAPI app

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Add to test file: `tests/test_health.py`
- [ ] Write unit tests for GET /api/health
  - [ ] Test returns 200 on success
  - [ ] Test returns Neo4j connection status
  - [ ] Test response format matches spec
  - [ ] Test when Neo4j connected
  - [ ] Test when Neo4j disconnected
  - [ ] Test no authentication required
- [ ] Run tests: `pytest tests/test_health.py -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Implement in: `app/routers/health.py`
- [ ] Create router instance
- [ ] Implement GET /health endpoint
  - [ ] Check Neo4j connectivity
  - [ ] Return health status with neo4j field
  - [ ] Include timestamp
- [ ] Add HealthResponse model to app/models.py
- [ ] Register router in app/main.py
- [ ] Run tests: `pytest tests/test_health.py::test_health* -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR - Improve Code Quality
- [ ] Run black: `black app/ tests/`
- [ ] Run ruff: `ruff check app/ tests/ --fix`
- [ ] Run mypy: `mypy app/`
- [ ] **Verify tests still pass** ✅

### 4️⃣ BDD Validation (if applicable)
- [ ] Run related BDD scenarios: `behave features/health.feature --tags=@health -v`
- [ ] **Verify BDD scenarios pass** ✅

### 5️⃣ Coverage Check
- [ ] Run coverage: `pytest tests/test_health.py --cov=app.routers.health --cov-report=term-missing`
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] GET /api/health endpoint implemented
- [ ] Returns 200 status code
- [ ] Returns health status JSON
- [ ] Includes Neo4j connection status
- [ ] Includes timestamp
- [ ] No authentication required
- [ ] Response matches specification format

### Non-Functional Requirements
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage
- [ ] Type hints present (mypy compliant)
- [ ] Code formatted (black)
- [ ] Linting passed (ruff)
- [ ] BDD scenarios pass
- [ ] Documentation (docstrings)

### Code Quality Gates
- [ ] Pre-commit hooks pass
- [ ] All pytest tests pass
- [ ] Coverage >= 100%
- [ ] No mypy errors
- [ ] No ruff warnings

---

## Implementation Notes

### Files to Create/Modify
```
app/routers/health.py (implement)
app/models.py (add HealthResponse)
app/main.py (register router)
tests/test_health.py (add tests)
```

### Example Code Structure

**app/models.py additions:**
```python
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Overall health status")
    neo4j: dict[str, Any] = Field(..., description="Neo4j connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**app/routers/health.py:**
```python
"""Health and database listing endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.dependencies import get_neo4j_client
from app.models import HealthResponse
from app.utils.neo4j_client import Neo4jClient

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    client: Neo4jClient = Depends(get_neo4j_client),
) -> HealthResponse:
    """Health check endpoint.

    Returns API health status and Neo4j connectivity.
    This endpoint does NOT require authentication.

    Returns:
        Health status including Neo4j connection state.
    """
    connected = client.verify_connectivity()

    return HealthResponse(
        status="healthy" if connected else "degraded",
        neo4j={
            "connected": connected,
            "uri": client.settings.neo4j_uri,
        },
        timestamp=datetime.now(timezone.utc),
    )
```

**app/main.py additions:**
```python
from app.routers import health

app.include_router(health.router)
```

### Testing Strategy

**Unit tests:**
- Test endpoint returns 200
- Test response format
- Test Neo4j connected status
- Test Neo4j disconnected status
- Test no authentication required
- Mock Neo4j client connectivity

---

## Git Workflow

### Start Issue
```bash
git checkout main
git pull origin main
git checkout -b issue/10-health-check-endpoint
```

### During Development
```bash
# TDD cycle
pytest tests/test_health.py -v  # FAIL
# Implement
pytest tests/test_health.py -v  # PASS

# Refactor
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# BDD validation
behave features/health.feature --tags=@health -v

# Commit
git add app/routers/health.py app/models.py app/main.py tests/test_health.py
git commit -m "feat(issue-10): implement GET /api/health endpoint"

# Push
git push origin issue/10-health-check-endpoint
```

### Create Pull Request
```bash
gh pr create \
  --title "feat: implement health check endpoint" \
  --body "$(cat <<'EOF'
## Summary
- Implemented GET /api/health endpoint
- Returns Neo4j connectivity status
- No authentication required
- Full test coverage

## Changes
- Created health router with /health endpoint
- Added HealthResponse model
- Registered router in main app
- Complete unit and BDD test coverage

## Testing
- [x] Unit tests pass (pytest)
- [x] BDD tests pass (behave)
- [x] 100% coverage achieved
- [x] Pre-commit hooks pass

## Closes
Closes #10

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### After Merge
```bash
mv issues/10-health-check-endpoint.md issues/completed/
git checkout main
git pull origin main
```

---

## Verification Commands

```bash
# Run unit tests
pytest tests/test_health.py -v

# Run BDD scenarios
behave features/health.feature --tags=@health -v

# Test endpoint manually
curl http://localhost:8000/api/health
```

---

## References
- **Specification:** `specs/endpoints-health.md`
- **BDD Feature:** `features/health.feature`
- **Data Models:** `specs/data-models.md`

---

## Notes
- This endpoint MUST NOT require authentication (public endpoint)
- Health check is used by monitoring systems
- Should return quickly (< 1 second)
- Consider caching Neo4j connectivity check for performance
