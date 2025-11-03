# Issue 18: Implement Node Search Endpoint

## Status
⏳ **TODO**

**Estimated Time:** 3 hours
**Branch:** `issue/18-search-node-endpoint`
**Phase:** 4 - Search Endpoints

## Description
Implement `GET /api/{database}/search/node/full` endpoint in `app/routers/search.py` for fuzzy node search with pagination.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-search.md` - Section 1 (Node Search)

## Related BDD Tests
- [ ] **Feature file:** `features/search.feature`
- [ ] **Tags:** `@search`, `@node`

## Dependencies
- [ ] Issue #17 - Search models

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Create: `tests/test_search.py`
- [ ] Write tests for GET /api/{database}/search/node/full
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement
- [ ] Create: `app/routers/search.py`
- [ ] Implement node search with fuzzy matching
- [ ] Register router in app/main.py
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR & BDD
- [ ] Run black, ruff, mypy
- [ ] Run: `behave features/search.feature --tags=@node -v`
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] GET /api/{database}/search/node/full endpoint
- [ ] Query parameter: q (search term)
- [ ] Query parameter: limit (default 100)
- [ ] Query parameter: skip (default 0)
- [ ] Fuzzy matching on node properties
- [ ] Returns SearchResponse with nodes
- [ ] Requires authentication

---

## Implementation Notes

```python
"""Node and edge search endpoints."""

from fastapi import APIRouter, Depends, Query, Path

from app.dependencies import get_neo4j_client, verify_api_key
from app.models import SearchResponse, Node
from app.utils.neo4j_client import Neo4jClient

router = APIRouter(
    prefix="/api/{database}/search",
    tags=["search"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/node/full", response_model=SearchResponse)
async def search_nodes(
    database: str = Path(...),
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    client: Neo4jClient = Depends(get_neo4j_client),
) -> SearchResponse:
    """Search nodes with fuzzy matching.

    Args:
        database: Target database.
        q: Search term.
        limit: Maximum results.
        skip: Skip results (pagination).
        client: Neo4j client.

    Returns:
        Search results with matching nodes.
    """
    # Cypher query with case-insensitive CONTAINS matching
    query = """
    MATCH (n)
    WHERE any(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($query))
    RETURN n
    SKIP $skip
    LIMIT $limit
    """

    results = client.execute_query(
        query=query,
        parameters={"query": q, "skip": skip, "limit": limit},
        database=database,
    )

    nodes = [
        Node(
            id=str(record["n"].id),
            categories=list(record["n"].labels),
            properties=dict(record["n"]),
        )
        for record in results
    ]

    return SearchResponse(nodes=nodes, edges=[], count=len(nodes))
```

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/18-search-node-endpoint

# TDD, implement, test
pytest tests/test_search.py -v
behave features/search.feature --tags=@node -v

# Commit
git add app/routers/search.py app/main.py tests/test_search.py
git commit -m "feat(issue-18): implement node search endpoint with fuzzy matching"
git push origin issue/18-search-node-endpoint
```

---

## References
- **Specification:** `specs/endpoints-search.md` - Section 1

---

## Notes
- Fuzzy matching uses CONTAINS for substring search
- Case-insensitive search improves UX
- Pagination via skip/limit parameters
