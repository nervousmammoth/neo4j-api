# Issues - Ticket-Based Development Workflow

This directory contains all development tasks organized as small, manageable tickets following Test-Driven Development (TDD) principles.

## Overview

**Total Tickets:** 36 (00-35)
**Phases:** 8 phases from Foundation to Deployment
**Average Time:** 1.7-2.4 hours per ticket
**Total Estimated Time:** 60-85 hours

## Directory Structure

```
issues/
├── README.md                    # This file - workflow overview
├── templates/
│   └── ticket-template.md       # Template for creating new tickets
├── 00-create-readme.md          # Active tickets (TODO or IN PROGRESS)
├── 01-create-env-example.md
├── ... (other active tickets)
└── completed/
    └── XX-ticket-name.md        # Completed and merged tickets
```

## Ticket Lifecycle

```
📝 Created → 🚧 In Progress → 🔍 PR Review → ✅ Merged → 📦 Moved to completed/
```

### Ticket States

Each ticket has a status indicator at the top:
- ⏳ **TODO** - Not started yet
- 🚧 **IN PROGRESS** - Currently being worked on
- ✅ **COMPLETED** - Finished and merged to main

## All Tickets by Phase

### Phase 0: Foundation (00-03)
**Goal:** Setup project structure and documentation

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 00 | create-readme | 1h | ⏳ TODO | None |
| 01 | create-env-example | 0.5h | ⏳ TODO | None |
| 02 | setup-app-structure | 0.5h | ⏳ TODO | None |
| 03 | setup-tests-structure | 0.5h | ⏳ TODO | #02 |

**Phase Total:** 2.5 hours

---

### Phase 1: Core Infrastructure (04-09)
**Goal:** Implement foundational modules (config, Neo4j client, validators, auth)

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 04 | config-module | 1h | ⏳ TODO | #03 |
| 05 | neo4j-client | 2h | ⏳ TODO | #04 |
| 06 | query-validator | 2h | ⏳ TODO | #03 |
| 07 | pydantic-models-base | 1h | ⏳ TODO | #03 |
| 08 | api-key-dependency | 1.5h | ⏳ TODO | #04 |
| 09 | fastapi-app-skeleton | 2h | ⏳ TODO | #04, #05, #08 |

**Phase Total:** 9.5 hours

**Critical:** Issue #06 (query-validator) is security-critical - blocks write operations

---

### Phase 2: Health Endpoints (10-12)
**Goal:** Implement health check and database listing endpoints

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 10 | health-check-endpoint | 1.5h | ⏳ TODO | #09 |
| 11 | databases-list-endpoint | 1.5h | ⏳ TODO | #09 |
| 12 | health-bdd-validation | 1h | ⏳ TODO | #10, #11 |

**Phase Total:** 4 hours

**BDD Coverage:** 12 scenarios in `features/health.feature`

---

### Phase 3: Query Execution (13-16)
**Goal:** Implement Cypher query execution with read-only validation

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 13 | query-models | 1h | ⏳ TODO | #07 |
| 14 | query-endpoint-basic | 2h | ⏳ TODO | #09, #13 |
| 15 | query-validation-integration | 2h | ⏳ TODO | #06, #14 |
| 16 | query-bdd-validation | 1h | ⏳ TODO | #15 |

**Phase Total:** 6 hours

**BDD Coverage:** 18 scenarios in `features/query.feature`

---

### Phase 4: Search Endpoints (17-20)
**Goal:** Implement node and edge search with fuzzy matching

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 17 | search-models | 1h | ⏳ TODO | #07 |
| 18 | search-node-endpoint | 2h | ⏳ TODO | #09, #17 |
| 19 | search-edge-endpoint | 2h | ⏳ TODO | #09, #17 |
| 20 | search-bdd-validation | 1h | ⏳ TODO | #18, #19 |

**Phase Total:** 6 hours

**BDD Coverage:** 19 scenarios in `features/search.feature`

---

### Phase 5: Node Operations (21-25)
**Goal:** Implement node retrieval, expansion, and counting operations

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 21 | node-models | 1.5h | ⏳ TODO | #07 |
| 22 | get-node-endpoint | 1.5h | ⏳ TODO | #09, #21 |
| 23 | expand-node-endpoint | 2h | ⏳ TODO | #09, #21 |
| 24 | count-endpoints | 1.5h | ⏳ TODO | #09, #21 |
| 25 | nodes-bdd-validation | 1h | ⏳ TODO | #22, #23, #24 |

**Phase Total:** 7.5 hours

**BDD Coverage:** 15 scenarios in `features/nodes.feature`

---

### Phase 6: Schema Endpoints (26-29)
**Goal:** Implement schema discovery (node labels, relationship types)

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 26 | schema-models | 1h | ⏳ TODO | #07 |
| 27 | schema-node-types-endpoint | 1.5h | ⏳ TODO | #09, #26 |
| 28 | schema-edge-types-endpoint | 1.5h | ⏳ TODO | #09, #26 |
| 29 | schema-bdd-validation | 1h | ⏳ TODO | #27, #28 |

**Phase Total:** 5 hours

**BDD Coverage:** 14 scenarios in `features/schema.feature`

---

### Phase 7: Integration & Polish (30-32)
**Goal:** Validate complete system with full BDD suite and coverage

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 30 | auth-bdd-validation | 1h | ⏳ TODO | #08, #09 |
| 31 | full-bdd-suite | 2h | ⏳ TODO | All features |
| 32 | coverage-verification | 1h | ⏳ TODO | All implementation |

**Phase Total:** 4 hours

**BDD Coverage:** All 91 scenarios across 6 feature files

---

### Phase 8: Deployment (33-35)
**Goal:** Production deployment configuration and documentation

| # | Ticket | Est. Time | Status | Dependencies |
|---|--------|-----------|--------|--------------|
| 33 | caddyfile-config | 1h | ⏳ TODO | #32 |
| 34 | systemd-service | 1h | ⏳ TODO | #32 |
| 35 | deployment-docs | 2h | ⏳ TODO | #33, #34 |

**Phase Total:** 4 hours

---

## Quick Start

### 1. View Available Tickets

```bash
# List all active tickets
ls -1 issues/*.md

# View next ticket to work on (lowest number)
ls -1 issues/*.md | head -1

# View ticket details
cat issues/00-create-readme.md

# Check completed tickets
ls -1 issues/completed/
```

### 2. Start Working on a Ticket

```bash
# Read the ticket
cat issues/XX-ticket-name.md

# Check dependencies (in ticket file)
# Make sure dependency tickets are completed

# Create branch
git checkout main
git pull origin main
git checkout -b issue/XX-ticket-name
```

### 3. Follow TDD Workflow

**For Implementation Tickets (follow Red → Green → Refactor):**

```bash
# RED - Write failing tests
# 1. Create test file: tests/test_module.py
# 2. Write tests that should pass once feature is implemented
# 3. Run: pytest tests/test_module.py -v
# 4. Verify: Tests FAIL ❌

# GREEN - Implement minimum code
# 1. Create/edit implementation file: app/module.py
# 2. Write code to make tests pass
# 3. Run: pytest tests/test_module.py -v
# 4. Verify: Tests PASS ✅

# REFACTOR - Improve code quality
# 1. Run: black app/ tests/
# 2. Run: ruff check app/ tests/ --fix
# 3. Run: mypy app/
# 4. Run tests again - verify still PASS ✅
```

**For Validation Tickets:**

```bash
# Run BDD scenarios
behave features/your_feature.feature -v

# Verify all scenarios pass
# Check coverage report
pytest --cov=app --cov-report=term-missing
```

### 4. Quality Checks

```bash
# Run all unit tests with coverage
pytest --cov=app --cov-fail-under=100 --cov-report=html

# Run BDD smoke tests
behave features/ --tags=@smoke

# Run all pre-commit hooks
pre-commit run --all-files

# Full test suite (unit + BDD + quality)
./scripts/run_all_tests.sh
```

### 5. Commit and Push

```bash
# Stage changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "feat(issue-XX): implement feature"

# Push to remote
git push origin issue/XX-ticket-name
```

### 6. Create Pull Request

```bash
gh pr create \
  --title "feat: [Ticket title]" \
  --body "$(cat <<'EOF'
## Summary
- [What was implemented]

## Changes
- [List of changes]

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

### 7. After Merge

```bash
# Move ticket to completed
mv issues/XX-ticket-name.md issues/completed/

# Update local main branch
git checkout main
git pull origin main

# Ready for next ticket!
ls -1 issues/*.md | head -1
```

## Progress Tracking

### Check Progress

```bash
# Count total tickets
ls -1 issues/*.md 2>/dev/null | wc -l

# Count completed tickets
ls -1 issues/completed/*.md 2>/dev/null | wc -l

# Calculate percentage complete
echo "scale=2; $(ls -1 issues/completed/*.md 2>/dev/null | wc -l) / 36 * 100" | bc

# View progress by phase
for phase in {0..8}; do
  start=$((phase * 10 / 3))
  count=$(ls -1 issues/completed/${start}*.md 2>/dev/null | wc -l)
  echo "Phase $phase: $count tickets completed"
done
```

### Visualize Dependencies

**Phase 0-1 Dependencies:**
```
00 ─┐
01 ─┼─→ (Foundation complete)
02 ─┤
    ├─→ 03 → 04 → 05 ─┐
    │         │        ├─→ 09 (App skeleton)
    │         ├─→ 06 ──┤
    │         └─→ 08 ──┘
    └─→ 07 ─────────────┘
```

**Phase 2-3 Dependencies:**
```
09 ─┬─→ 10 ─┐
    │        ├─→ 12 (Health BDD)
    └─→ 11 ─┘

07 → 13 → 14 → 15 → 16 (Query BDD)
06 ────────────┘
```

**Phase 4-6 Dependencies:**
```
09 + 07 → 17 → 18 ─┐
                19 ─┼─→ 20 (Search BDD)

09 + 07 → 21 → 22 ─┐
               23 ─┼─→ 25 (Nodes BDD)
               24 ─┘

09 + 07 → 26 → 27 ─┐
               28 ─┼─→ 29 (Schema BDD)
```

## Ticket Template

To create a new ticket (if needed):

```bash
# Copy template
cp issues/templates/ticket-template.md issues/XX-new-feature.md

# Edit with ticket details
nano issues/XX-new-feature.md
```

## Tips for Efficient Workflow

### 1. Read Specs First
Always check the specification before starting:
- `specs/endpoints-*.md` - Endpoint behavior
- `specs/data-models.md` - Request/response models
- `specs/error-handling.md` - Error responses

### 2. Check BDD Tests
Review feature files to understand expected behavior:
- `features/*.feature` - Gherkin scenarios
- `features/steps/` - Step definitions

### 3. Follow TDD Strictly
**Always write tests first:**
1. Write failing test (RED)
2. Implement minimum code (GREEN)
3. Refactor for quality (REFACTOR)
4. Repeat

### 4. Use Existing Fixtures
Reuse test fixtures from `tests/conftest.py`:
- `client` - FastAPI TestClient
- `mock_neo4j_driver` - Mocked Neo4j driver
- `api_key` - Valid API key
- `sample_node_data` - Sample node for testing

### 5. Mock Neo4j Driver
**In unit tests:** Always mock `GraphDatabase.driver`
```python
from unittest.mock import patch

@patch('app.utils.neo4j_client.GraphDatabase.driver')
def test_feature(mock_driver):
    # Your test here
```

### 6. Check Dependencies
Before starting a ticket:
```bash
# Check ticket dependencies section
grep "## Dependencies" issues/XX-ticket-name.md -A 5

# Verify dependencies are completed
ls -1 issues/completed/ | grep "^05-"
```

### 7. Commit Frequently
Small, focused commits are better:
```bash
# After RED phase
git commit -m "test(issue-XX): add failing tests for feature"

# After GREEN phase
git commit -m "feat(issue-XX): implement feature to pass tests"

# After REFACTOR phase
git commit -m "refactor(issue-XX): improve code quality"
```

### 8. Keep Tests Green
Never move to the next step if tests are failing:
- RED phase: Tests should FAIL (expected)
- GREEN phase: Tests should PASS
- REFACTOR phase: Tests should still PASS
- Before commit: All tests should PASS

### 9. Watch Coverage
Maintain 100% coverage throughout:
```bash
# After each implementation
pytest --cov=app --cov-fail-under=100 --cov-report=term-missing

# Check specific module
pytest tests/test_module.py --cov=app.module --cov-report=term-missing
```

### 10. Run Smoke Tests Often
Quick sanity check:
```bash
# Takes ~1 minute
behave features/ --tags=@smoke
```

## Quality Gates

Every ticket must pass these gates before PR:

### ✅ Code Quality
- [ ] Black formatting applied
- [ ] Ruff linting passed (no warnings)
- [ ] mypy type checking passed (no errors)
- [ ] Bandit security scan passed

### ✅ Testing
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage for new code
- [ ] BDD scenarios pass (if applicable)
- [ ] All existing tests still pass

### ✅ Documentation
- [ ] Docstrings present (Google style)
- [ ] Type hints on all functions
- [ ] Comments for complex logic

### ✅ Git Hygiene
- [ ] Commits follow conventional commit format
- [ ] Commit messages clear and descriptive
- [ ] Pre-commit hooks pass
- [ ] Branch up-to-date with main

## Troubleshooting

### Issue: Pre-commit hooks failing
```bash
pre-commit run --all-files
# Fix reported issues
pre-commit autoupdate
```

### Issue: Coverage below 100%
```bash
pytest --cov=app --cov-report=html
xdg-open htmlcov/index.html  # View detailed report
# Add tests for uncovered lines
```

### Issue: BDD tests failing
```bash
behave features/your_feature.feature -v
# Check mock setup in features/environment.py
# Verify endpoint implementation matches specification
```

### Issue: Merge conflicts
```bash
git checkout main && git pull
git checkout issue/XX-ticket-name
git merge main
# Resolve conflicts
git add . && git commit
```

## References

- **Development Guide:** `../CLAUDE.md` - Complete development workflow
- **Specifications:** `../specs/` - API specifications
- **BDD Tests:** `../features/` - Behavior-driven test scenarios
- **Implementation Plan:** `../IMPLEMENTATION_PLAN.md` - Detailed roadmap

## Project Status

**Current Phase:** Foundation (Phase 0)
**Tickets Completed:** 0/36
**Tickets In Progress:** 0
**Tickets Remaining:** 36

**Next Ticket:** #00 - create-readme

Start working: `cat issues/00-create-readme.md`
