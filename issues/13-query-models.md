# Issue 13: Implement Query Request/Response Models

## Status
⏳ **TODO**

**Estimated Time:** 1-2 hours
**Branch:** `issue/13-query-models`
**Phase:** 3 - Query Execution

## Description
Implement Pydantic models for query execution in `app/models.py`: QueryRequest and QueryResponse following Linkurious format.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-query.md` - Section 2 (Query Execution)
- [ ] **Spec file:** `specs/data-models.md` - Section 3 (Query Models)

## Related BDD Tests
- [ ] **Feature file:** `features/query.feature`
- [ ] All query scenarios use these models

## Dependencies
- [ ] Issue #07 - Base models exist

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Add to: `tests/test_models.py`
- [ ] Write tests for QueryRequest
  - [ ] Test with query only
  - [ ] Test with query and parameters
  - [ ] Test parameter validation
- [ ] Write tests for QueryResponse
  - [ ] Test with results
  - [ ] Test with execution metadata
- [ ] Run tests: `pytest tests/test_models.py::test_query* -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Add to: `app/models.py`
- [ ] Implement QueryRequest model
- [ ] Implement QueryResponse model
- [ ] Run tests: `pytest tests/test_models.py::test_query* -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR
- [ ] Run black, ruff, mypy
- [ ] **Verify tests still pass** ✅

### 5️⃣ Coverage Check
- [ ] Run coverage
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] QueryRequest model with query and parameters fields
- [ ] QueryResponse model with results and metadata
- [ ] Field validation
- [ ] JSON serialization

### Non-Functional Requirements
- [ ] Unit tests with 100% coverage
- [ ] Type hints, formatting, linting

---

## Implementation Notes

### Example Code

```python
class QueryRequest(BaseModel):
    """Cypher query execution request.

    Attributes:
        query: Cypher query string.
        parameters: Query parameters (optional).
    """

    query: str = Field(..., description="Cypher query string", min_length=1)
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Query parameters"
    )

    model_config = {"json_schema_extra": {"example": {
        "query": "MATCH (n:Person) WHERE n.name = $name RETURN n LIMIT 10",
        "parameters": {"name": "John"}
    }}}


class QueryResponse(BaseModel):
    """Cypher query execution response.

    Attributes:
        results: Query result records.
        count: Number of records returned.
        execution_time_ms: Query execution time in milliseconds.
    """

    results: list[dict[str, Any]] = Field(..., description="Query results")
    count: int = Field(..., ge=0, description="Number of records")
    execution_time_ms: float = Field(..., ge=0, description="Execution time (ms)")

    model_config = {"json_schema_extra": {"example": {
        "results": [{"n": {"name": "John", "age": 30}}],
        "count": 1,
        "execution_time_ms": 15.3
    }}}
```

---

## Git Workflow

```bash
git checkout main
git pull origin main
git checkout -b issue/13-query-models

# TDD cycle
pytest tests/test_models.py::test_query* -v

# Implement
# Refactor
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# Commit
git add app/models.py tests/test_models.py
git commit -m "feat(issue-13): implement query request/response models"
git push origin issue/13-query-models
```

---

## Verification Commands

```bash
pytest tests/test_models.py -v
python -c "from app.models import QueryRequest, QueryResponse; print('Models OK')"
```

---

## References
- **Specification:** `specs/endpoints-query.md`
- **Data Models:** `specs/data-models.md`

---

## Notes
- Models follow Linkurious API format
- Parameters field defaults to empty dict
- Execution time tracking will be implemented in endpoint
