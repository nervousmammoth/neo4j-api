# Issue 16: Validate Query Endpoints with BDD Suite

## Status
⏳ **TODO**

**Estimated Time:** 1 hour
**Branch:** `issue/16-query-bdd-validation`
**Phase:** 3 - Query Execution

## Description
Run and validate all BDD scenarios in `features/query.feature` (18 scenarios) to ensure query execution endpoint meets acceptance criteria. Fix any failing scenarios.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-query.md`

## Related BDD Tests
- [ ] **Feature file:** `features/query.feature`
- [ ] **Scenarios:** All 18 scenarios
- [ ] **Tags:** `@query`, `@validation`, `@critical`

## Dependencies
- [ ] Issue #14 - Query endpoint basic implementation
- [ ] Issue #15 - Query validation integration

---

## Workflow Checklist

### 1️⃣ Run BDD Suite
- [ ] Run all query scenarios: `behave features/query.feature -v`
- [ ] Document which scenarios pass/fail
- [ ] Identify root causes of failures

### 2️⃣ Fix Failing Scenarios
- [ ] Fix implementation issues
- [ ] Fix test data issues
- [ ] Fix step definition issues
- [ ] Re-run after each fix

### 3️⃣ Verify All Pass
- [ ] Run: `behave features/query.feature -v`
- [ ] **Verify all 18 scenarios PASS** ✅
- [ ] Run critical tests: `behave features/query.feature --tags=@critical -v`
- [ ] **Verify critical tests PASS** ✅

### 4️⃣ Documentation
- [ ] Document any spec clarifications needed
- [ ] Document any test updates made
- [ ] Update issue with results

---

## Acceptance Criteria

### Functional Requirements
- [ ] All 18 scenarios in query.feature pass
- [ ] Query execution works correctly
- [ ] Query validation blocks write operations
- [ ] Parameterized queries work
- [ ] Multi-database support works
- [ ] Authentication required
- [ ] Response formats match specifications

### Verification Requirements
- [ ] BDD suite runs without errors
- [ ] All scenarios pass consistently
- [ ] Critical tests pass
- [ ] No regressions in other features

---

## Implementation Notes

### BDD Scenarios to Validate

**From features/query.feature (18 scenarios):**

**Basic Execution:**
1. Execute simple MATCH query
2. Execute query with RETURN
3. Execute query with LIMIT
4. Execute query with WHERE clause
5. Query with parameters
6. Query with multiple parameters

**Validation (Critical):**
7. CREATE query is rejected (400)
8. DELETE query is rejected
9. MERGE query is rejected
10. SET query is rejected
11. REMOVE query is rejected
12. DETACH DELETE is rejected

**Advanced:**
13. Query with OPTIONAL MATCH
14. Query with WITH clause
15. Query on different database
16. Query requires authentication
17. Query execution time tracked
18. Empty result set

### Expected Results

All 18 scenarios should pass. Common issues:
- **Validation failures** - Ensure validator is called before execution
- **Response format** - Check QueryResponse model serialization
- **Authentication** - Ensure dependency is applied
- **Database routing** - Check path parameter handling

---

## Git Workflow

```bash
git checkout main
git pull origin main
git checkout -b issue/16-query-bdd-validation

# Run BDD suite
behave features/query.feature -v

# Fix any issues (commits as needed)
git add [files]
git commit -m "fix(issue-16): [description of fix]"

# Final validation
behave features/query.feature -v
behave features/ --tags=@critical -v

# Document results
git commit -m "test(issue-16): validate query BDD scenarios (18/18 passing)"
git push origin issue/16-query-bdd-validation
```

---

## Verification Commands

```bash
# Run all query scenarios
behave features/query.feature -v

# Run critical validation tests
behave features/query.feature --tags=@critical -v

# Run specific scenario
behave features/query.feature:15 -v

# Run with verbose output
behave features/query.feature -v --no-capture
```

---

## References
- **BDD Feature:** `features/query.feature`
- **Specification:** `specs/endpoints-query.md`
- **Implementation:** Issues #14, #15

---

## Notes
- This is a validation/verification issue
- All scenarios should pass if endpoint is correctly implemented
- Pay special attention to validation scenarios (critical security)
- This completes Phase 3 (Query Execution)
