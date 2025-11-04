# Issue 28: Implement Edge Types Schema Endpoint

## Status
⏳ **TODO**

**Estimated Time:** 1-2 hours
**Branch:** `issue/28-schema-edge-types-endpoint`
**Phase:** 6 - Schema Endpoints

## Description
Implement `GET /api/{database}/graph/schema/edge/types` endpoint to retrieve all relationship types from the database schema.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-schema.md` - Section 2 (Edge Types)

## Related BDD Tests
- [ ] **Feature file:** `features/schema.feature`
- [ ] **Tags:** `@schema`, `@edge_types`

## Dependencies
- [ ] Issue #27 - Schema router exists

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Add to: `tests/test_schema.py`
- [ ] Write tests for GET /api/{database}/graph/schema/edge/types
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement
- [ ] Add to: `app/routers/schema.py`
- [ ] Implement edge types endpoint
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR & BDD
- [ ] Run black, ruff, mypy
- [ ] Run: `behave features/schema.feature --tags=@edge_types -v`
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] GET /api/{database}/graph/schema/edge/types endpoint
- [ ] Returns EdgeTypeResponse with all types
- [ ] Requires authentication

---

## Implementation Notes

```python
@router.get("/edge/types", response_model=EdgeTypeResponse)
async def get_edge_types(
    database: str = Path(...),
    client: Neo4jClient = Depends(get_neo4j_client),
) -> EdgeTypeResponse:
    """Get all relationship types in the database."""

    query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
    results = client.execute_query(query=query, database=database)

    types = [record["relationshipType"] for record in results]

    return EdgeTypeResponse(types=types, count=len(types))
```

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/28-schema-edge-types-endpoint

# TDD, implement, test
pytest tests/test_schema.py::test_edge_types* -v
behave features/schema.feature --tags=@edge_types -v

# Commit
git add app/routers/schema.py tests/test_schema.py
git commit -m "feat(issue-28): implement edge types schema endpoint"
git push origin issue/28-schema-edge-types-endpoint
```

---

## References
- **Specification:** `specs/endpoints-schema.md` - Section 2
