# Issue 30: Validate Authentication with BDD Suite

## Status
⏳ **TODO**

**Estimated Time:** 1 hour
**Branch:** `issue/30-auth-bdd-validation`
**Phase:** 7 - Integration & Polish

## Description
Run and validate all BDD scenarios in `features/authentication.feature` (13 scenarios) to ensure authentication works correctly across all endpoints.

## Related Specifications
- [ ] **Spec file:** `specs/authentication.md`

## Related BDD Tests
- [ ] **Feature file:** `features/authentication.feature`
- [ ] **Scenarios:** All 13 scenarios
- [ ] **Tags:** `@auth`, `@critical`

## Dependencies
- [ ] All endpoint implementations complete (Issues #10-28)

---

## Workflow Checklist

### 1️⃣ Run BDD Suite
- [ ] Run: `behave features/authentication.feature -v`
- [ ] Document pass/fail results

### 2️⃣ Fix Failing Scenarios
- [ ] Fix implementation/test issues
- [ ] Re-run after fixes

### 3️⃣ Verify All Pass
- [ ] Run: `behave features/authentication.feature -v`
- [ ] **Verify all 13 scenarios PASS** ✅

---

## Acceptance Criteria

### Verification Requirements
- [ ] All 13 scenarios pass
- [ ] Authentication works on all protected endpoints
- [ ] Public endpoints don't require authentication
- [ ] Invalid keys are rejected
- [ ] Missing keys are rejected
- [ ] Valid keys allow access

---

## BDD Scenarios to Validate

**Authentication Tests (13 scenarios):**
1. Valid API key allows access to query endpoint
2. Valid API key allows access to search endpoint
3. Valid API key allows access to node endpoint
4. Valid API key allows access to schema endpoint
5. Invalid API key is rejected (401)
6. Missing API key is rejected (401)
7. Empty API key is rejected (401)
8. Health endpoint does not require authentication
9. Databases endpoint does not require authentication
10. Authentication header is case-insensitive
11. Authentication error message is clear
12. Multiple requests with same key work
13. Authentication across different databases

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/30-auth-bdd-validation

# Run BDD suite
behave features/authentication.feature -v

# Fix issues as needed
# Final validation
behave features/authentication.feature -v
behave features/ --tags=@critical -v

# Commit
git commit -m "test(issue-30): validate authentication BDD scenarios (13/13 passing)"
git push origin issue/30-auth-bdd-validation
```

---

## Verification Commands

```bash
# Run all authentication scenarios
behave features/authentication.feature -v

# Run critical tests
behave features/authentication.feature --tags=@critical -v

# Run specific scenario
behave features/authentication.feature:10 -v
```

---

## References
- **BDD Feature:** `features/authentication.feature`
- **Specification:** `specs/authentication.md`
- **Implementation:** Issue #08

---

## Notes
- This validates authentication works end-to-end across all endpoints
- Critical security validation
- Ensures public endpoints remain public
- Ensures protected endpoints require auth
