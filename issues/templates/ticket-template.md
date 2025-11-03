# Issue [XX]: [Title]

## Status
⏳ **TODO** | 🚧 **IN PROGRESS** | ✅ **COMPLETED**

**Estimated Time:** [1-3 hours]
**Branch:** `issue/XX-ticket-name`
**Phase:** [0-8]

## Description
[Brief description of what needs to be implemented]

## Related Specifications
- [ ] **Spec file:** `specs/[filename].md` - Section [X.X]
- [ ] **Data models:** `specs/data-models.md` - Section [X.X]
- [ ] **Error handling:** `specs/error-handling.md` - Section [X.X]

## Related BDD Tests
- [ ] **Feature file:** `features/[feature].feature`
- [ ] **Scenarios:** [List relevant scenario names]
- [ ] **Tags:** `@tag1`, `@tag2`

## Dependencies
- [ ] Issue #[XX] - [Description]
- [ ] Issue #[XX] - [Description]

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Create test file: `tests/test_[module].py`
- [ ] Write unit tests for [functionality]
  - [ ] Test case: [description]
  - [ ] Test case: [description]
  - [ ] Test case: [description]
- [ ] Run tests: `pytest tests/test_[module].py -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Create implementation file: `app/[module].py`
- [ ] Implement [functionality]
  - [ ] [Specific implementation step]
  - [ ] [Specific implementation step]
- [ ] Run tests: `pytest tests/test_[module].py -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR - Improve Code Quality
- [ ] Run black: `black app/ tests/`
- [ ] Run ruff: `ruff check app/ tests/ --fix`
- [ ] Run mypy: `mypy app/`
- [ ] **Verify tests still pass** ✅

### 4️⃣ BDD Validation (if applicable)
- [ ] Run related BDD scenarios: `behave features/[feature].feature -v`
- [ ] **Verify BDD scenarios pass** ✅

### 5️⃣ Coverage Check
- [ ] Run coverage: `pytest --cov=app --cov-report=term-missing --cov-report=html`
- [ ] **Verify 100% coverage** for new code ✅
- [ ] Check HTML report: `open htmlcov/index.html`

---

## Acceptance Criteria

### Functional Requirements
- [ ] [Requirement 1]
- [ ] [Requirement 2]
- [ ] [Requirement 3]

### Non-Functional Requirements
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage for new code
- [ ] Type hints present (mypy compliant)
- [ ] Code formatted (black)
- [ ] Linting passed (ruff)
- [ ] No security issues (bandit)
- [ ] BDD scenarios pass (if applicable)
- [ ] Documentation updated (docstrings)

### Code Quality Gates
- [ ] Pre-commit hooks pass
- [ ] All pytest tests pass
- [ ] Coverage >= 100% for new code
- [ ] No mypy errors
- [ ] No ruff warnings

---

## Implementation Notes

### Files to Create
```
[List files to be created]
```

### Files to Modify
```
[List files to be modified]
```

### Key Implementation Details
- [Detail 1]
- [Detail 2]
- [Detail 3]

### Example Code Structure
```python
# Example implementation outline
```

### Testing Strategy
- **Unit tests:** [description]
- **Mocking approach:** [description]
- **Edge cases:** [list edge cases to test]

---

## Git Workflow

### Start Issue
```bash
git checkout main
git pull origin main
git checkout -b issue/XX-ticket-name
```

### During Development
```bash
# Make changes, run TDD cycle

# Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat(issue-XX): [concise description]"

# Push
git push origin issue/XX-ticket-name
```

### Create Pull Request
```bash
gh pr create \
  --title "feat: [Title]" \
  --body "$(cat <<'EOF'
## Summary
- [Summary point 1]
- [Summary point 2]

## Changes
- [Change 1]
- [Change 2]

## Testing
- [x] Unit tests pass (pytest)
- [x] BDD tests pass (behave)
- [x] 100% coverage achieved
- [x] Pre-commit hooks pass

## Closes
Closes #XX

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### After Merge
```bash
# Move ticket to completed
mv issues/XX-ticket-name.md issues/completed/

# Update local main
git checkout main
git pull origin main
```

---

## Verification Commands

```bash
# Run unit tests
pytest tests/test_[module].py -v

# Run with coverage
pytest tests/test_[module].py --cov=app.[module] --cov-report=term-missing

# Run BDD scenarios
behave features/[feature].feature -v

# Run smoke tests
behave features/ --tags=@smoke

# Run all quality checks
pre-commit run --all-files

# Verify no regressions
./scripts/run_all_tests.sh
```

---

## References
- **Specification:** `specs/[filename].md`
- **BDD Feature:** `features/[feature].feature`
- **Implementation Plan:** `IMPLEMENTATION_PLAN.md` - Phase [X]
- **Related Issues:** #[XX], #[XX]

---

## Notes
[Any additional notes, gotchas, or important considerations]
