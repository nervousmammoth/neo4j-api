# Issue 25: Validate Node Endpoints with BDD Suite

## Status
⏳ **TODO**

**Estimated Time:** 1 hour
**Branch:** `issue/25-nodes-bdd-validation`
**Phase:** 5 - Node Operations

## Description
Run and validate all BDD scenarios in `features/nodes.feature` (15 scenarios) to ensure node operation endpoints meet acceptance criteria.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-nodes.md`

## Related BDD Tests
- [ ] **Feature file:** `features/nodes.feature`
- [ ] **Scenarios:** All 15 scenarios
- [ ] **Tags:** `@nodes`, `@get`, `@expand`, `@count`

## Dependencies
- [ ] Issue #22 - Get node endpoint
- [ ] Issue #23 - Expand node endpoint
- [ ] Issue #24 - Count endpoints

---

## Workflow Checklist

### 1️⃣ Run BDD Suite
- [ ] Run: `behave features/nodes.feature -v`
- [ ] Document pass/fail results

### 2️⃣ Fix Failing Scenarios
- [ ] Fix implementation/test issues
- [ ] Re-run after fixes

### 3️⃣ Verify All Pass
- [ ] Run: `behave features/nodes.feature -v`
- [ ] **Verify all 15 scenarios PASS** ✅

---

## Acceptance Criteria

### Verification Requirements
- [ ] All 15 scenarios pass
- [ ] Get node endpoint works
- [ ] Expand endpoint works
- [ ] Count endpoints work
- [ ] Authentication required
- [ ] No regressions

---

## BDD Scenarios to Validate

**Get Node (4 scenarios):**
1. Get node by valid ID returns node
2. Get node by invalid ID returns 404
3. Get node returns correct format
4. Get node requires authentication

**Expand Neighborhood (6 scenarios):**
5. Expand node returns neighbors
6. Expand with direction "in"
7. Expand with direction "out"
8. Expand with direction "both"
9. Expand multiple nodes
10. Expand requires authentication

**Count (5 scenarios):**
11. Count nodes returns total
12. Count edges returns total
13. Count on empty database returns 0
14. Count requires authentication
15. Count on different databases

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/25-nodes-bdd-validation

# Run BDD suite
behave features/nodes.feature -v

# Fix issues as needed
# Final validation
behave features/nodes.feature -v

# Commit
git commit -m "test(issue-25): validate node operation BDD scenarios (15/15 passing)"
git push origin issue/25-nodes-bdd-validation
```

---

## Verification Commands

```bash
behave features/nodes.feature -v
behave features/nodes.feature --tags=@nodes -v
behave features/nodes.feature --tags=@get -v
behave features/nodes.feature --tags=@expand -v
behave features/nodes.feature --tags=@count -v
```

---

## Notes
- Validation/verification issue
- Completes Phase 5 (Node Operations)
