# Issue 24: Implement Node/Edge Count Endpoints

## Status
⏳ **TODO**

**Estimated Time:** 1-2 hours
**Branch:** `issue/24-count-endpoints`
**Phase:** 5 - Node Operations

## Description
Implement count endpoints: `GET /api/{database}/graph/nodes/count` and `GET /api/{database}/graph/edges/count`.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-nodes.md` - Sections 3-4 (Count Operations)

## Related BDD Tests
- [ ] **Feature file:** `features/nodes.feature`
- [ ] **Tags:** `@nodes`, `@count`

## Dependencies
- [ ] Issue #21 - CountResponse model

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Add to: `tests/test_nodes.py`
- [ ] Write tests for count endpoints
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement
- [ ] Add to: `app/routers/nodes.py`
- [ ] Implement both count endpoints
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR & BDD
- [ ] Run black, ruff, mypy
- [ ] Run: `behave features/nodes.feature --tags=@count -v`
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] GET /api/{database}/graph/nodes/count endpoint
- [ ] GET /api/{database}/graph/edges/count endpoint
- [ ] Returns CountResponse
- [ ] Requires authentication

---

## Implementation Notes

```python
@router.get("/nodes/count", response_model=CountResponse)
async def count_nodes(
    database: str = Path(...),
    client: Neo4jClient = Depends(get_neo4j_client),
) -> CountResponse:
    """Count all nodes in database."""

    query = "MATCH (n) RETURN count(n) as count"
    results = client.execute_query(query=query, database=database)

    return CountResponse(count=results[0]["count"])


@router.get("/edges/count", response_model=CountResponse)
async def count_edges(
    database: str = Path(...),
    client: Neo4jClient = Depends(get_neo4j_client),
) -> CountResponse:
    """Count all relationships in database."""

    query = "MATCH ()-[r]->() RETURN count(r) as count"
    results = client.execute_query(query=query, database=database)

    return CountResponse(count=results[0]["count"])
```

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/24-count-endpoints

# TDD, implement, test
pytest tests/test_nodes.py::test_count* -v
behave features/nodes.feature --tags=@count -v

# Commit
git add app/routers/nodes.py tests/test_nodes.py
git commit -m "feat(issue-24): implement node and edge count endpoints"
git push origin issue/24-count-endpoints
```

---

## References
- **Specification:** `specs/endpoints-nodes.md` - Sections 3-4
