# Issue 29: Validate Schema Endpoints with BDD Suite

## Status
⏳ **TODO**

**Estimated Time:** 1 hour
**Branch:** `issue/29-schema-bdd-validation`
**Phase:** 6 - Schema Endpoints

## Description
Run and validate all BDD scenarios in `features/schema.feature` (14 scenarios) to ensure schema discovery endpoints meet acceptance criteria.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-schema.md`

## Related BDD Tests
- [ ] **Feature file:** `features/schema.feature`
- [ ] **Scenarios:** All 14 scenarios
- [ ] **Tags:** `@schema`, `@node_types`, `@edge_types`

## Dependencies
- [ ] Issue #27 - Node types endpoint
- [ ] Issue #28 - Edge types endpoint

---

## Workflow Checklist

### 1️⃣ Run BDD Suite
- [ ] Run: `behave features/schema.feature -v`
- [ ] Document pass/fail results

### 2️⃣ Fix Failing Scenarios
- [ ] Fix implementation/test issues
- [ ] Re-run after fixes

### 3️⃣ Verify All Pass
- [ ] Run: `behave features/schema.feature -v`
- [ ] **Verify all 14 scenarios PASS** ✅

---

## Acceptance Criteria

### Verification Requirements
- [ ] All 14 scenarios pass
- [ ] Node types endpoint works
- [ ] Edge types endpoint works
- [ ] Authentication required
- [ ] No regressions

---

## BDD Scenarios to Validate

**Node Types (7 scenarios):**
1. Get node types returns all labels
2. Node types format is correct
3. Node types count is accurate
4. Node types on empty database
5. Node types requires authentication
6. Node types on different database
7. Node types with multiple labels

**Edge Types (7 scenarios):**
8. Get edge types returns all types
9. Edge types format is correct
10. Edge types count is accurate
11. Edge types on empty database
12. Edge types requires authentication
13. Edge types on different database
14. Edge types with multiple types

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/29-schema-bdd-validation

# Run BDD suite
behave features/schema.feature -v

# Fix issues as needed
# Final validation
behave features/schema.feature -v

# Commit
git commit -m "test(issue-29): validate schema BDD scenarios (14/14 passing)"
git push origin issue/29-schema-bdd-validation
```

---

## Verification Commands

```bash
behave features/schema.feature -v
behave features/schema.feature --tags=@schema -v
behave features/schema.feature --tags=@node_types -v
behave features/schema.feature --tags=@edge_types -v
```

---

## Notes
- Validation/verification issue
- Completes Phase 6 (Schema Endpoints)
