# Issues - Priority-Based Development Workflow

This directory contains all development tasks organized as prioritized tickets following Test-Driven Development (TDD) principles.

## Overview

**Naming Schema:** `P{priority}.{number}-Title-With-Dashes.md`
**Priority Levels:** P0 (Foundation/Done) → P1 (High) → P2 (Medium) → P3 (Lower) → P4 (Infrastructure)

## Directory Structure

```
issues/
├── README.md                         # This file - workflow overview
├── templates/
│   └── ticket-template.md            # Template for creating new tickets
├── P1.1-Query-Models.md              # Active tickets by priority
├── P2.1-Search-Models.md
├── ... (other active tickets)
└── completed/
    └── P0.X-Ticket-Name.md           # Completed and merged tickets
```

## Ticket Format

Each ticket uses YAML-style frontmatter:

```markdown
---
**Status:** To Do | In Progress | Done
**Priority:** P0 | P1 | P2 | P3 | P4
**Branch:** `feature/P{X}.{Y}-Title-Name`
---

## Overview

Description of the ticket...
```

## All Tickets by Priority

### P0 - Foundation (Completed)
**Goal:** Setup project structure and core infrastructure

| Code | Title | Status |
|------|-------|--------|
| P0.0 | Create-Readme | ✅ Done |
| P0.1 | Create-Env-Example | ✅ Done |
| P0.2 | Setup-App-Structure | ✅ Done |
| P0.3 | Setup-Tests-Structure | ✅ Done |
| P0.4 | Config-Module | ✅ Done |
| P0.5 | Neo4j-Client | ✅ Done |
| P0.6 | Query-Validator | ✅ Done |
| P0.7 | Pydantic-Models-Base | ✅ Done |
| P0.8 | API-Key-Dependency | ✅ Done |
| P0.9 | FastAPI-App-Skeleton | ✅ Done |
| P0.10 | Health-Check-Endpoint | ✅ Done |
| P0.11 | Databases-List-Endpoint | ✅ Done |

---

### P1 - Query Execution & Fixes (High Priority)
**Goal:** Implement query execution and fix critical issues

| Code | Title | Status | Dependencies |
|------|-------|--------|--------------|
| P1.1 | Query-Models | ⏳ To Do | P0.7 |
| P1.2 | Query-Endpoint-Basic | ⏳ To Do | P0.5, P0.8, P1.1 |
| P1.3 | Query-Validation-Integration | ⏳ To Do | P0.6, P1.2 |
| P1.4 | Fix-Coverage-Config | ⏳ To Do | None |
| P1.5 | Standardize-Error-Format | ⏳ To Do | None |
| P1.6 | Fix-Health-Response-Types | ⏳ To Do | None |

---

### P2 - Search & Node Endpoints (Medium Priority)
**Goal:** Implement search and node operations

| Code | Title | Status | Dependencies |
|------|-------|--------|--------------|
| P2.1 | Search-Models | ⏳ To Do | P0.7 |
| P2.2 | Search-Node-Endpoint | ⏳ To Do | P0.9, P2.1 |
| P2.3 | Search-Edge-Endpoint | ⏳ To Do | P0.9, P2.1 |
| P2.4 | Node-Models | ⏳ To Do | P0.7 |
| P2.5 | Get-Node-Endpoint | ⏳ To Do | P0.9, P2.4 |
| P2.6 | Expand-Node-Endpoint | ⏳ To Do | P0.9, P2.4 |
| P2.7 | Count-Endpoints | ⏳ To Do | P0.9, P2.4 |

---

### P3 - Schema Endpoints (Lower Priority)
**Goal:** Implement schema discovery

| Code | Title | Status | Dependencies |
|------|-------|--------|--------------|
| P3.1 | Schema-Models | ⏳ To Do | P0.7 |
| P3.2 | Schema-Node-Types-Endpoint | ⏳ To Do | P0.9, P3.1 |
| P3.3 | Schema-Edge-Types-Endpoint | ⏳ To Do | P0.9, P3.1 |

---

### P4 - Infrastructure & Deployment
**Goal:** Production deployment and documentation

| Code | Title | Status | Dependencies |
|------|-------|--------|--------------|
| P4.1 | Coverage-Verification | ⏳ To Do | All P1-P3 |
| P4.2 | Caddyfile-Config | ⏳ To Do | P4.1 |
| P4.3 | Systemd-Service | ⏳ To Do | P4.1 |
| P4.4 | Deployment-Docs | ⏳ To Do | P4.2, P4.3 |
| P4.5 | Integration-Tests-Docker | ⏳ To Do | P4.1 |
| P4.6 | Housekeeping-Docs | ⏳ To Do | None |

---

## Quick Start

### 1. View Available Tickets

```bash
# List all active tickets by priority
ls -1 issues/P*.md

# View next high-priority ticket
ls -1 issues/P1*.md | head -1

# View ticket details
cat issues/P1.1-Query-Models.md

# Check completed tickets
ls -1 issues/completed/
```

### 2. Start Working on a Ticket

```bash
# Read the ticket
cat issues/P1.1-Query-Models.md

# Check dependencies (in ticket file)
# Make sure dependency tickets are completed

# Create branch
git checkout main
git pull origin main
git checkout -b feature/P1.1-Query-Models
```

### 3. Follow TDD Workflow

**RED → GREEN → REFACTOR:**

```bash
# RED - Write failing tests
pytest tests/test_module.py -v  # Should FAIL

# GREEN - Implement minimum code
pytest tests/test_module.py -v  # Should PASS

# REFACTOR - Improve code quality
black app/ tests/
ruff check app/ tests/ --fix
mypy app/
pytest tests/test_module.py -v  # Should still PASS
```

### 4. Commit and Push

```bash
# Commit (pre-commit hooks run automatically)
git commit -m "feat(P1.1): implement query models"

# Push to remote
git push origin feature/P1.1-Query-Models
```

### 5. Create Pull Request

```bash
gh pr create \
  --title "feat(P1.1): implement query models" \
  --body "## Summary
- Implemented QueryRequest and QueryResponse models

## Closes
Closes P1.1

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

### 6. After Merge

```bash
# Move ticket to completed
mv issues/P1.1-Query-Models.md issues/completed/

# Update local main branch
git checkout main
git pull origin main
```

## Progress Tracking

```bash
# Count active tickets
ls -1 issues/P*.md 2>/dev/null | wc -l

# Count completed tickets
ls -1 issues/completed/*.md 2>/dev/null | wc -l

# List by priority
echo "P1 (High):" && ls issues/P1*.md 2>/dev/null | wc -l
echo "P2 (Medium):" && ls issues/P2*.md 2>/dev/null | wc -l
echo "P3 (Lower):" && ls issues/P3*.md 2>/dev/null | wc -l
echo "P4 (Infrastructure):" && ls issues/P4*.md 2>/dev/null | wc -l
```

## Quality Gates

Every ticket must pass before PR:

- [ ] Black formatting applied
- [ ] Ruff linting passed
- [ ] mypy type checking passed
- [ ] Unit tests written (TDD)
- [ ] 100% code coverage
- [ ] Pre-commit hooks pass

## References

- **Development Guide:** `../CLAUDE.md`
- **Specifications:** `../specs/`
- **BDD Tests:** `../features/`

## Project Status

**Completed:** 12 (P0.0-P0.11)
**Active:** 22 (P1-P4)
**Next Priority:** P1 - Query Execution & Fixes
