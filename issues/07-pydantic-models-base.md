# Issue 07: Implement Base Pydantic Response Models

## Status
⏳ **TODO**

**Estimated Time:** 2 hours
**Branch:** `issue/07-pydantic-models-base`
**Phase:** 1 - Core Infrastructure

## Description
Implement base Pydantic response models in `app/models.py` including ErrorResponse and SuccessResponse. These models follow the Linkurious API format and will be used across all endpoints.

## Related Specifications
- [ ] **Spec file:** `specs/data-models.md` - Section 2 (Base Response Models)
- [ ] **Spec file:** `specs/error-handling.md` - Error response format
- [ ] **Reference:** All endpoint specs for response format examples

## Related BDD Tests
All feature files use error responses:
- [ ] **Feature files:** `features/*.feature`
- [ ] **Tags:** `@error`

## Dependencies
None - Base models are foundational

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Create test section in: `tests/test_models.py`
- [ ] Write unit tests for ErrorResponse
  - [ ] Test model instantiation
  - [ ] Test JSON serialization
  - [ ] Test field validation
  - [ ] Test model_dump() output
- [ ] Write unit tests for SuccessResponse
  - [ ] Test model instantiation
  - [ ] Test JSON serialization
  - [ ] Test field validation
- [ ] Run tests: `pytest tests/test_models.py -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Add to implementation file: `app/models.py`
- [ ] Implement ErrorResponse model
  - [ ] Add error field
  - [ ] Add message field
  - [ ] Add optional details field
  - [ ] Add status_code field
- [ ] Implement SuccessResponse model
  - [ ] Add success field
  - [ ] Add optional message field
- [ ] Add model configuration
- [ ] Run tests: `pytest tests/test_models.py -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR - Improve Code Quality
- [ ] Run black: `black app/ tests/`
- [ ] Run ruff: `ruff check app/ tests/ --fix`
- [ ] Run mypy: `mypy app/`
- [ ] **Verify tests still pass** ✅

### 4️⃣ BDD Validation (if applicable)
N/A - Will be validated when endpoints are implemented

### 5️⃣ Coverage Check
- [ ] Run coverage: `pytest tests/test_models.py --cov=app.models --cov-report=term-missing`
- [ ] **Verify 100% coverage** for new code ✅

---

## Acceptance Criteria

### Functional Requirements
- [ ] ErrorResponse model implemented
- [ ] SuccessResponse model implemented
- [ ] Models follow Linkurious API format
- [ ] JSON serialization works correctly
- [ ] Field validation present
- [ ] Type hints on all fields
- [ ] Docstrings with examples

### Non-Functional Requirements
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage for new code
- [ ] Type hints present (mypy compliant)
- [ ] Code formatted (black)
- [ ] Linting passed (ruff)
- [ ] Documentation updated (docstrings)

### Code Quality Gates
- [ ] Pre-commit hooks pass
- [ ] All pytest tests pass
- [ ] Coverage >= 100% for new code
- [ ] No mypy errors
- [ ] No ruff warnings

---

## Implementation Notes

### Files to Create/Modify
```
app/models.py (add to existing file)
tests/test_models.py (create new file)
```

### Example Code Structure

```python
"""Pydantic models for request and response data.

This module contains all data models following Linkurious API format.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model.

    Used for all error responses across the API.

    Attributes:
        error: Error type/code.
        message: Human-readable error message.
        details: Optional additional error details.
        status_code: HTTP status code.

    Examples:
        >>> error = ErrorResponse(
        ...     error="ValidationError",
        ...     message="Query contains forbidden write operations",
        ...     status_code=400
        ... )
    """

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        default=None, description="Additional error details"
    )
    status_code: int = Field(..., ge=400, le=599, description="HTTP status code")

    model_config = {"json_schema_extra": {"example": {
        "error": "ValidationError",
        "message": "Invalid query",
        "status_code": 400
    }}}


class SuccessResponse(BaseModel):
    """Generic success response model.

    Used for simple success responses without data payload.

    Attributes:
        success: Success indicator (always True).
        message: Optional success message.

    Examples:
        >>> response = SuccessResponse(success=True, message="Operation completed")
    """

    success: bool = Field(default=True, description="Success indicator")
    message: str | None = Field(default=None, description="Optional success message")

    model_config = {"json_schema_extra": {"example": {
        "success": True,
        "message": "Operation completed successfully"
    }}}
```

### Testing Strategy

**Unit tests for ErrorResponse:**
- Test creating instance with required fields
- Test JSON serialization with model_dump()
- Test status_code validation (must be >= 400)
- Test with optional details field
- Test field types are validated

**Unit tests for SuccessResponse:**
- Test creating instance with defaults
- Test with custom message
- Test JSON serialization
- Test success field is always True

---

## Git Workflow

### Start Issue
```bash
git checkout main
git pull origin main
git checkout -b issue/07-pydantic-models-base
```

### During Development
```bash
# TDD: Write tests first
# Run pytest tests/test_models.py -v (should FAIL)

# Implement models
# Run pytest tests/test_models.py -v (should PASS)

# Refactor
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# Commit
git add app/models.py tests/test_models.py
git commit -m "feat(issue-07): implement base Pydantic response models"

# Push
git push origin issue/07-pydantic-models-base
```

### Create Pull Request
```bash
gh pr create \
  --title "feat: implement base Pydantic response models" \
  --body "$(cat <<'EOF'
## Summary
- Implemented ErrorResponse and SuccessResponse models
- Follows Linkurious API format
- Full test coverage

## Changes
- Created ErrorResponse model with error, message, details, status_code
- Created SuccessResponse model
- Added comprehensive unit tests
- 100% test coverage

## Testing
- [x] Unit tests pass (pytest)
- [x] 100% coverage achieved
- [x] Pre-commit hooks pass

## Closes
Closes #07

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### After Merge
```bash
mv issues/07-pydantic-models-base.md issues/completed/
git checkout main
git pull origin main
```

---

## Verification Commands

```bash
# Run unit tests
pytest tests/test_models.py -v

# Run with coverage
pytest tests/test_models.py --cov=app.models --cov-report=term-missing

# Test model usage
python -c "
from app.models import ErrorResponse, SuccessResponse
error = ErrorResponse(error='TestError', message='Test', status_code=400)
print('ErrorResponse:', error.model_dump())
success = SuccessResponse(message='Success')
print('SuccessResponse:', success.model_dump())
"
```

---

## References
- **Specification:** `specs/data-models.md`
- **Error Handling:** `specs/error-handling.md`
- **Pydantic docs:** https://docs.pydantic.dev/

---

## Notes
- These base models will be used by all endpoints
- More specific models (Node, Edge, Query, etc.) will be added in later issues
- Models should be JSON-serializable for FastAPI responses
- Follow Pydantic v2 conventions
