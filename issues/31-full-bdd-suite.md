# Issue 31: Run Complete BDD Test Suite

## Status
⏳ **TODO**

**Estimated Time:** 1-2 hours
**Branch:** `issue/31-full-bdd-suite`
**Phase:** 7 - Integration & Polish

## Description
Run the complete BDD test suite (all 91 scenarios across 6 feature files) to ensure the entire API meets all acceptance criteria. This is the final integration test before deployment.

## Related Specifications
- [ ] All specification files in `specs/`

## Related BDD Tests
- [ ] **All feature files:**
  - `features/health.feature` (12 scenarios)
  - `features/authentication.feature` (13 scenarios)
  - `features/query.feature` (18 scenarios)
  - `features/search.feature` (19 scenarios)
  - `features/nodes.feature` (15 scenarios)
  - `features/schema.feature` (14 scenarios)
- [ ] **Total:** 91 scenarios

## Dependencies
- [ ] All feature implementations complete (Issues #10-28)
- [ ] All individual BDD validations complete (Issues #12, #16, #20, #25, #29, #30)

---

## Workflow Checklist

### 1️⃣ Run Complete Suite
- [ ] Run: `behave features/ -v`
- [ ] Document total pass/fail results by feature
- [ ] Identify any failing scenarios

### 2️⃣ Fix Any Regressions
- [ ] Review and fix any failing scenarios
- [ ] Ensure no regressions from individual validations
- [ ] Re-run after each fix

### 3️⃣ Run Smoke Tests
- [ ] Run: `behave features/ --tags=@smoke -v`
- [ ] **Verify all smoke tests PASS** ✅

### 4️⃣ Run Critical Tests
- [ ] Run: `behave features/ --tags=@critical -v`
- [ ] **Verify all critical tests PASS** ✅

### 5️⃣ Final Validation
- [ ] Run: `behave features/ -v`
- [ ] **Verify all 91 scenarios PASS** ✅
- [ ] Generate BDD test report

---

## Acceptance Criteria

### Verification Requirements
- [ ] All 91 scenarios pass
- [ ] All smoke tests pass
- [ ] All critical tests pass
- [ ] No regressions
- [ ] Test execution time reasonable (< 5 minutes)
- [ ] All features tested:
  - [ ] Health (12/12)
  - [ ] Authentication (13/13)
  - [ ] Query (18/18)
  - [ ] Search (19/19)
  - [ ] Nodes (15/15)
  - [ ] Schema (14/14)

---

## Implementation Notes

### Test Suite Structure

**By Feature:**
- **Health:** `/api/health`, `/api/databases` (12 scenarios)
- **Authentication:** API key validation (13 scenarios)
- **Query:** Cypher execution and validation (18 scenarios)
- **Search:** Node/edge search (19 scenarios)
- **Nodes:** Get, expand, count operations (15 scenarios)
- **Schema:** Node/edge type discovery (14 scenarios)

**By Tag:**
- `@smoke` - Critical smoke tests (~20 scenarios)
- `@critical` - High-priority tests (~30 scenarios)
- `@error` - Error handling tests
- `@validation` - Query validation tests (security)
- `@auth` - Authentication tests

### Running Strategies

**Full suite:**
```bash
behave features/ -v
```

**By feature:**
```bash
behave features/health.feature -v
behave features/authentication.feature -v
behave features/query.feature -v
behave features/search.feature -v
behave features/nodes.feature -v
behave features/schema.feature -v
```

**By tag:**
```bash
behave features/ --tags=@smoke -v
behave features/ --tags=@critical -v
behave features/ --tags=@error -v
behave features/ --tags=@validation -v
```

**Generate report:**
```bash
behave features/ --format=json --outfile=bdd-report.json
behave features/ --format=html --outfile=bdd-report.html
```

---

## Git Workflow

```bash
git checkout main && git pull origin main
git checkout -b issue/31-full-bdd-suite

# Run complete suite
behave features/ -v > bdd-results.txt

# Run smoke tests
behave features/ --tags=@smoke -v

# Run critical tests
behave features/ --tags=@critical -v

# Fix any issues
# Re-run suite
behave features/ -v

# Generate report
behave features/ --format=json --outfile=bdd-report.json

# Document results
echo "BDD Test Results:" >> issues/31-full-bdd-suite.md
echo "==================" >> issues/31-full-bdd-suite.md
grep "scenarios passed" bdd-results.txt >> issues/31-full-bdd-suite.md

# Commit
git add issues/31-full-bdd-suite.md bdd-report.json
git commit -m "test(issue-31): validate complete BDD suite (91/91 scenarios passing)"
git push origin issue/31-full-bdd-suite
```

### Create Pull Request

```bash
gh pr create \
  --title "test: validate complete BDD test suite" \
  --body "$(cat <<'EOF'
## Summary
- Ran complete BDD test suite (91 scenarios)
- All features validated end-to-end
- Smoke and critical tests passing

## Test Results
- Health: 12/12 ✅
- Authentication: 13/13 ✅
- Query: 18/18 ✅
- Search: 19/19 ✅
- Nodes: 15/15 ✅
- Schema: 14/14 ✅
- **Total: 91/91 ✅**

## Changes
- [List any fixes made, if any]
- [Or: No changes needed - all tests passed]

## Testing
- [x] Complete BDD suite passes (91/91)
- [x] Smoke tests pass
- [x] Critical tests pass
- [x] No regressions

## Closes
Closes #31

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Verification Commands

```bash
# Complete suite
behave features/ -v

# Summary only
behave features/ --no-capture --format=progress

# Smoke tests
behave features/ --tags=@smoke -v

# Critical tests
behave features/ --tags=@critical -v

# Count scenarios
behave features/ --dry-run | grep scenarios

# Generate JSON report
behave features/ --format=json --outfile=bdd-report.json

# Generate HTML report (if behave-html-formatter installed)
behave features/ --format=html --outfile=bdd-report.html
```

---

## References
- **All BDD Features:** `features/*.feature`
- **All Specifications:** `specs/*.md`
- **BDD Setup:** `BDD_SETUP_SUMMARY.md`
- **Features README:** `features/README.md`

---

## Notes
- This is the final comprehensive validation before deployment
- All 91 scenarios must pass before moving to deployment phase
- This validates the entire API end-to-end
- Smoke tests should run quickly (< 1 minute)
- Complete suite should run in < 5 minutes
- Generate test report for documentation
- This completes Phase 7 Integration Testing
