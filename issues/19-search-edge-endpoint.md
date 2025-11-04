# Issue 19: Implement Edge Search Endpoint

## Status
⏳ **TODO**

**Estimated Time:** 2-3 hours
**Branch:** `issue/19-search-edge-endpoint`
**Phase:** 4 - Search Endpoints

## Description
Implement `GET /api/{database}/search/edge/full` endpoint in `app/routers/search.py` for relationship search with pagination.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-search.md` - Section 2 (Edge Search)

## Related BDD Tests
- [ ] **Feature file:** `features/search.feature`
- [ ] **Tags:** `@search`, `@edge`

## Dependencies
- [ ] Issue #18 - Search router exists

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Add to: `tests/test_search.py`
- [ ] Write tests for GET /api/{database}/search/edge/full
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement
- [ ] Add to: `app/routers/search.py`
- [ ] Implement edge search with fuzzy matching
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR & BDD
- [ ] Run black, ruff, mypy
- [ ] Run: `behave features/search.feature --tags=@edge -v`
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] GET /api/{database}/search/edge/full endpoint
- [ ] Query parameters: q, limit, skip
- [ ] Fuzzy matching on edge properties
- [ ] Returns SearchResponse with edges
- [ ] Requires authentication

---

## Implementation Notes

```python
@router.get("/edge/full", response_model=SearchResponse)
async def search_edges(
    database: str = Path(...),
    q: str = Query(..., min_length=1),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    client: Neo4jClient = Depends(get_neo4j_client),
) -> SearchResponse:
    """Search edges/relationships with fuzzy matching."""

    query = """
    MATCH (source)-[r]->(target)
    WHERE any(prop IN keys(r) WHERE toLower(toString(r[prop])) CONTAINS toLower($query))
    RETURN r, source, target
    SKIP $skip
    LIMIT $limit
    """

    results = client.execute_query(
        query=query,
        parameters={"query": q, "skip": skip, "limit": limit},
        database=database,
    )

    edges = [
        Edge(
            id=str(record["r"].id),
            type=record["r"].type,
            source=str(record["source"].id),
            target=str(record["target"].id),
            properties=dict(record["r"]),
        )
        for record in results
    ]

    return SearchResponse(nodes=[], edges=edges, count=len(edges))
```

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/19-search-edge-endpoint

# TDD, implement, test
pytest tests/test_search.py::test_*edge* -v
behave features/search.feature --tags=@edge -v

# Commit
git add app/routers/search.py tests/test_search.py
git commit -m "feat(issue-19): implement edge search endpoint with fuzzy matching"
git push origin issue/19-search-edge-endpoint
```

---

## References
- **Specification:** `specs/endpoints-search.md` - Section 2

---

## Notes
- Edge search includes source/target node IDs
- Similar fuzzy matching logic as node search
- Returns edges array in SearchResponse
