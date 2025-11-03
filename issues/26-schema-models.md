# Issue 26: Implement Schema Response Models

## Status
⏳ **TODO**

**Estimated Time:** 1 hour
**Branch:** `issue/26-schema-models`
**Phase:** 6 - Schema Endpoints

## Description
Implement Pydantic models for schema discovery: NodeTypeResponse, EdgeTypeResponse.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-schema.md`
- [ ] **Spec file:** `specs/data-models.md` - Section 6 (Schema Models)

## Related BDD Tests
- [ ] **Feature file:** `features/schema.feature`

## Dependencies
- [ ] Issue #07 - Base models

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Add to: `tests/test_models.py`
- [ ] Write tests for schema models
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement
- [ ] Add to: `app/models.py`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR & Coverage
- [ ] Run black, ruff, mypy
- [ ] **Verify 100% coverage** ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] NodeTypeResponse model with labels list
- [ ] EdgeTypeResponse model with types list
- [ ] Field validation

---

## Implementation Notes

```python
class NodeTypeResponse(BaseModel):
    """Node labels/types response."""

    labels: list[str] = Field(..., description="List of node labels")
    count: int = Field(..., ge=0, description="Number of labels")


class EdgeTypeResponse(BaseModel):
    """Relationship types response."""

    types: list[str] = Field(..., description="List of relationship types")
    count: int = Field(..., ge=0, description="Number of types")
```

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/26-schema-models

# TDD, implement
pytest tests/test_models.py::test_schema* -v
black app/ tests/
mypy app/

# Commit
git add app/models.py tests/test_models.py
git commit -m "feat(issue-26): implement schema response models"
git push origin issue/26-schema-models
```

---

## References
- **Specification:** `specs/endpoints-schema.md`
- **Data Models:** `specs/data-models.md` - Section 6
