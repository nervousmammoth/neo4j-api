# Issue 15: Integrate Read-Only Query Validation

## Status
⏳ **TODO**

**Estimated Time:** 2 hours
**Branch:** `issue/15-query-validation-integration`
**Phase:** 3 - Query Execution

## Description
Integrate the read-only query validator from Issue #06 into the query execution endpoint. This adds critical security validation to block write operations.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-query.md` - Section 2.3 (Query Validation)
- [ ] **Spec file:** `specs/error-handling.md` - Section 3.5 (Validation Errors)

## Related BDD Tests
- [ ] **Feature file:** `features/query.feature`
- [ ] **Scenarios:** Write query validation scenarios
- [ ] **Tags:** `@validation`, `@critical`

## Dependencies
- [ ] Issue #06 - Query validator implemented
- [ ] Issue #14 - Query endpoint basic implementation

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Add to: `tests/test_query.py`
- [ ] Write tests for validation integration
  - [ ] Test CREATE query is rejected (400)
  - [ ] Test DELETE query is rejected
  - [ ] Test MERGE query is rejected
  - [ ] Test SET query is rejected
  - [ ] Test MATCH query is allowed
  - [ ] Test validation error message format
- [ ] Run tests: `pytest tests/test_query.py::test_*validation* -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Modify: `app/routers/query.py`
- [ ] Add validation before query execution
- [ ] Return 400 with clear error on write queries
- [ ] Run tests: `pytest tests/test_query.py -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR
- [ ] Run black, ruff, mypy
- [ ] **Verify tests still pass** ✅

### 4️⃣ BDD Validation
- [ ] Run: `behave features/query.feature --tags=@validation -v`
- [ ] **Verify validation scenarios pass** ✅

### 5️⃣ Coverage Check
- [ ] Run coverage
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] Query validation integrated into endpoint
- [ ] Write queries (CREATE, DELETE, etc.) return 400
- [ ] Read queries (MATCH, RETURN) execute normally
- [ ] Clear error messages for blocked queries
- [ ] Validation happens before query execution

### Non-Functional Requirements
- [ ] Unit tests with 100% coverage
- [ ] BDD validation scenarios pass
- [ ] Type hints, formatting, linting

---

## Implementation Notes

### Example Code

**app/routers/query.py modifications:**
```python
from app.utils.validators import is_read_only_query

@router.post("/query", response_model=QueryResponse)
async def execute_query(
    database: str = Path(..., description="Database name"),
    request: QueryRequest = ...,
    client: Neo4jClient = Depends(get_neo4j_client),
) -> QueryResponse:
    """Execute a read-only Cypher query.

    The query is validated to ensure it contains no write operations.

    Args:
        database: Target database name.
        request: Query request with query string and parameters.
        client: Neo4j client instance.

    Returns:
        Query results with execution metadata.

    Raises:
        HTTPException: If query validation fails or execution fails.
    """
    # Validate query is read-only
    if not is_read_only_query(request.query):
        raise HTTPException(
            status_code=400,
            detail=(
                "Query validation failed: Write operations are not allowed. "
                "Only read-only queries (MATCH, RETURN, WITH, CALL db.*, SHOW) "
                "are permitted."
            ),
        )

    try:
        start_time = time.time()

        results = client.execute_query(
            query=request.query,
            parameters=request.parameters,
            database=database,
        )

        execution_time_ms = (time.time() - start_time) * 1000

        return QueryResponse(
            results=results,
            count=len(results),
            execution_time_ms=round(execution_time_ms, 2),
        )

    except Neo4jError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {str(e)}",
        )
```

---

## Git Workflow

```bash
git checkout main
git pull origin main
git checkout -b issue/15-query-validation-integration

# TDD cycle
pytest tests/test_query.py::test_*validation* -v

# Implement validation
pytest tests/test_query.py -v

# Refactor
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# BDD validation
behave features/query.feature --tags=@validation -v

# Commit
git add app/routers/query.py tests/test_query.py
git commit -m "feat(issue-15): integrate read-only query validation (CRITICAL SECURITY)"
git push origin issue/15-query-validation-integration
```

---

## Verification Commands

```bash
pytest tests/test_query.py -v
behave features/query.feature --tags=@validation -v

# Test write query blocked
curl -X POST http://localhost:8000/api/neo4j/graph/query \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE (n:Person {name: \"Test\"}) RETURN n"}'
# Should return 400 error

# Test read query allowed
curl -X POST http://localhost:8000/api/neo4j/graph/query \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (n) RETURN n LIMIT 5"}'
# Should return results
```

---

## References
- **Specification:** `specs/endpoints-query.md` - Section 2.3
- **BDD Feature:** `features/query.feature`
- **Validator:** Issue #06

---

## Notes
- **CRITICAL SECURITY FEATURE** - This enforces the read-only API constraint
- Validation must happen BEFORE query execution
- Error message should be clear and helpful
- Consider logging blocked queries for security auditing
