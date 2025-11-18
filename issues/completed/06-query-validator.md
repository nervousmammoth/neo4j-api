# Issue 06: Implement Read-Only Query Validator (CRITICAL SECURITY)

## Status
⏳ **TODO**

**Estimated Time:** 2-3 hours
**Branch:** `issue/06-query-validator`
**Phase:** 1 - Core Infrastructure

## Description
Implement `app/utils/validators.py` with read-only query validation to ensure no write operations (CREATE, DELETE, MERGE, SET, REMOVE, DROP) are executed. This is a **CRITICAL SECURITY FEATURE** that enforces the API's read-only constraint.

## Related Specifications
- [ ] **Spec file:** `specs/endpoints-query.md` - Section 2.3 (Query Validation)
- [ ] **Spec file:** `specs/error-handling.md` - Section 3.5 (Validation Errors)
- [ ] **Reference:** `CLAUDE.md` - Read-only enforcement

## Related BDD Tests
- [ ] **Feature file:** `features/query.feature`
- [ ] **Scenarios:** "Write query is rejected", "Read query is allowed"
- [ ] **Tags:** `@critical`, `@query`, `@validation`

## Dependencies
None - This is a standalone utility module

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Create test file: `tests/test_validators.py`
- [ ] Write unit tests for is_read_only_query()
  - [ ] Test MATCH queries are allowed
  - [ ] Test RETURN queries are allowed
  - [ ] Test OPTIONAL MATCH allowed
  - [ ] Test WITH clause allowed
  - [ ] Test CALL db.* procedures allowed
  - [ ] Test SHOW commands allowed
  - [ ] Test CREATE queries are blocked
  - [ ] Test DELETE queries are blocked
  - [ ] Test MERGE queries are blocked
  - [ ] Test SET queries are blocked
  - [ ] Test REMOVE queries are blocked
  - [ ] Test DROP queries are blocked
  - [ ] Test DETACH DELETE blocked
  - [ ] Test mixed case queries
  - [ ] Test queries with comments
  - [ ] Test multi-line queries
  - [ ] Test queries with string literals containing keywords
- [ ] Run tests: `pytest tests/test_validators.py -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Create implementation file: `app/utils/validators.py`
- [ ] Implement is_read_only_query() function
  - [ ] Parse query to remove comments
  - [ ] Parse query to remove string literals
  - [ ] Check for forbidden keywords
  - [ ] Case-insensitive matching
  - [ ] Return True if read-only, False if write detected
- [ ] Run tests: `pytest tests/test_validators.py -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR - Improve Code Quality
- [ ] Run black: `black app/ tests/`
- [ ] Run ruff: `ruff check app/ tests/ --fix`
- [ ] Run mypy: `mypy app/`
- [ ] **Verify tests still pass** ✅

### 4️⃣ BDD Validation (if applicable)
- [ ] Run related BDD scenarios: `behave features/query.feature --tags=@validation -v`
- [ ] **Verify BDD scenarios pass** ✅

### 5️⃣ Coverage Check
- [ ] Run coverage: `pytest --cov=app.utils.validators --cov-report=term-missing --cov-report=html`
- [ ] **Verify 100% coverage** for new code ✅
- [ ] Check HTML report: `open htmlcov/index.html`

---

## Acceptance Criteria

### Functional Requirements
- [ ] is_read_only_query() function implemented
- [ ] Blocks CREATE queries
- [ ] Blocks DELETE queries (including DETACH DELETE)
- [ ] Blocks MERGE queries
- [ ] Blocks SET queries
- [ ] Blocks REMOVE queries
- [ ] Blocks DROP queries
- [ ] Allows MATCH queries
- [ ] Allows RETURN clauses
- [ ] Allows WITH clauses
- [ ] Allows OPTIONAL MATCH
- [ ] Allows CALL db.* procedures
- [ ] Allows SHOW commands
- [ ] Case-insensitive keyword detection
- [ ] Handles multi-line queries
- [ ] Ignores keywords in string literals
- [ ] Ignores keywords in comments

### Non-Functional Requirements
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage for new code
- [ ] Type hints present (mypy compliant)
- [ ] Code formatted (black)
- [ ] Linting passed (ruff)
- [ ] No security issues (bandit)
- [ ] BDD scenarios pass
- [ ] Documentation updated (docstrings)
- [ ] Clear error messages for blocked queries

### Code Quality Gates
- [ ] Pre-commit hooks pass
- [ ] All pytest tests pass
- [ ] Coverage >= 100% for new code
- [ ] No mypy errors
- [ ] No ruff warnings
- [ ] Security scan passes (bandit)

---

## Implementation Notes

### Files to Create
```
app/utils/validators.py
tests/test_validators.py
```

### Key Implementation Details

**Query validation approach:**
1. **Remove comments** - Strip out `//` and `/* */` style comments
2. **Remove string literals** - Strip out quoted strings (single/double quotes)
3. **Normalize whitespace** - Convert to uppercase for keyword matching
4. **Check for forbidden keywords** - Detect write operations
5. **Word boundary matching** - Ensure not matching substrings

**Forbidden keywords:**
- `CREATE` - Creating nodes/relationships
- `DELETE` - Deleting nodes/relationships
- `DETACH DELETE` - Detaching and deleting
- `MERGE` - Creating or matching
- `SET` - Setting properties
- `REMOVE` - Removing properties/labels
- `DROP` - Dropping indexes/constraints

**Allowed patterns:**
- `MATCH` - Reading data
- `RETURN` - Returning results
- `WITH` - Query composition
- `OPTIONAL MATCH` - Optional pattern matching
- `CALL db.*` - Read-only database procedures
- `SHOW` - Showing metadata

### Example Code Structure

```python
"""Query validation utilities.

This module provides read-only query validation to ensure no write
operations (CREATE, DELETE, MERGE, SET, REMOVE) are executed.
"""

from __future__ import annotations

import re
from typing import Pattern

# Forbidden write keywords (word boundaries required)
WRITE_KEYWORDS: list[str] = [
    r"\bCREATE\b",
    r"\bDELETE\b",
    r"\bMERGE\b",
    r"\bSET\b",
    r"\bREMOVE\b",
    r"\bDROP\b",
    r"\bDETACH\s+DELETE\b",
]

# Compile patterns for performance
WRITE_PATTERNS: list[Pattern[str]] = [
    re.compile(keyword, re.IGNORECASE) for keyword in WRITE_KEYWORDS
]


def _remove_comments(query: str) -> str:
    """Remove comments from Cypher query.

    Args:
        query: Cypher query string.

    Returns:
        Query with comments removed.
    """
    # Remove single-line comments
    query = re.sub(r"//.*?$", "", query, flags=re.MULTILINE)
    # Remove multi-line comments
    query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
    return query


def _remove_string_literals(query: str) -> str:
    """Remove string literals from query.

    This prevents false positives from keywords inside strings.

    Args:
        query: Cypher query string.

    Returns:
        Query with string literals removed.
    """
    # Remove single-quoted strings
    query = re.sub(r"'[^']*'", "", query)
    # Remove double-quoted strings
    query = re.sub(r'"[^"]*"', "", query)
    return query


def is_read_only_query(query: str) -> bool:
    """Check if a Cypher query is read-only.

    This function validates that the query does not contain any write
    operations such as CREATE, DELETE, MERGE, SET, REMOVE, or DROP.

    Args:
        query: Cypher query string to validate.

    Returns:
        True if query is read-only, False if write operations detected.

    Examples:
        >>> is_read_only_query("MATCH (n) RETURN n")
        True
        >>> is_read_only_query("CREATE (n:Person) RETURN n")
        False
        >>> is_read_only_query("MATCH (n) SET n.name = 'John'")
        False
    """
    if not query or not query.strip():
        return True  # Empty query is considered safe

    # Remove comments and string literals to avoid false positives
    cleaned_query = _remove_comments(query)
    cleaned_query = _remove_string_literals(cleaned_query)

    # Check for write keywords
    for pattern in WRITE_PATTERNS:
        if pattern.search(cleaned_query):
            return False

    return True
```

### Testing Strategy

**Unit tests - Allowed queries:**
- `MATCH (n) RETURN n`
- `MATCH (n:Person) WHERE n.age > 30 RETURN n`
- `OPTIONAL MATCH (n)-[r]-(m) RETURN n, r, m`
- `MATCH (n) WITH n MATCH (n)-[r]->(m) RETURN n, r, m`
- `CALL db.labels() YIELD label RETURN label`
- `SHOW DATABASES`
- Queries with "CREATE" in string literals
- Queries with "DELETE" in comments

**Unit tests - Blocked queries:**
- `CREATE (n:Person) RETURN n`
- `MATCH (n) DELETE n`
- `MATCH (n) DETACH DELETE n`
- `MERGE (n:Person {id: 1}) RETURN n`
- `MATCH (n) SET n.name = 'John'`
- `MATCH (n) REMOVE n.age`
- `DROP INDEX index_name`
- Mixed case: `CrEaTe (n:Person)`
- Multi-line queries with write operations

**Edge cases:**
- Empty query
- Query with only whitespace
- Query with "CREATE" in comment: `// CREATE is blocked`
- Query with "DELETE" in string: `MATCH (n) WHERE n.text = 'DELETE' RETURN n`
- Complex multi-line queries
- Queries with multiple forbidden keywords

---

## Git Workflow

### Start Issue
```bash
git checkout main
git pull origin main
git checkout -b issue/06-query-validator
```

### During Development
```bash
# TDD Cycle: Write tests first
# Create comprehensive tests in tests/test_validators.py
# Run pytest tests/test_validators.py -v (should FAIL)

# Implement app/utils/validators.py
# Run pytest tests/test_validators.py -v (should PASS)

# Refactor
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# Security scan
bandit -r app/utils/validators.py

# Verify coverage
pytest tests/test_validators.py --cov=app.utils.validators --cov-report=term-missing

# Run related BDD tests
behave features/query.feature --tags=@validation -v

# Commit
git add app/utils/validators.py tests/test_validators.py
git commit -m "feat(issue-06): implement read-only query validator (CRITICAL SECURITY)"

# Push
git push origin issue/06-query-validator
```

### Create Pull Request
```bash
gh pr create \
  --title "feat: implement read-only query validator (CRITICAL SECURITY)" \
  --body "$(cat <<'EOF'
## Summary
- Implemented read-only query validator (CRITICAL SECURITY)
- Blocks all write operations (CREATE, DELETE, MERGE, SET, REMOVE, DROP)
- Comprehensive unit tests with 100% coverage
- Handles edge cases (comments, string literals, multi-line)

## Changes
- Created is_read_only_query() validation function
- Blocks CREATE, DELETE, MERGE, SET, REMOVE, DROP keywords
- Removes comments and string literals before validation
- Case-insensitive keyword detection with word boundaries
- Full test coverage including edge cases

## Testing
- [x] Unit tests pass (pytest)
- [x] BDD tests pass (behave)
- [x] 100% coverage achieved
- [x] Security scan passed (bandit)
- [x] Pre-commit hooks pass

## Security Notes
This is a critical security feature that enforces the read-only API constraint.
All write operations are blocked at the validation layer.

## Closes
Closes #06

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### After Merge
```bash
mv issues/06-query-validator.md issues/completed/
git checkout main
git pull origin main
```

---

## Verification Commands

```bash
# Run unit tests
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/test_validators.py --cov=app.utils.validators --cov-report=term-missing

# Run BDD validation scenarios
behave features/query.feature --tags=@validation -v

# Security scan
bandit -r app/utils/validators.py

# Run all quality checks
pre-commit run --all-files

# Test validator directly
python -c "
from app.utils.validators import is_read_only_query
print('MATCH allowed:', is_read_only_query('MATCH (n) RETURN n'))
print('CREATE blocked:', not is_read_only_query('CREATE (n:Person)'))
"
```

---

## References
- **Specification:** `specs/endpoints-query.md` - Section 2.3
- **BDD Feature:** `features/query.feature`
- **Error Handling:** `specs/error-handling.md` - Section 3.5
- **Implementation Plan:** `IMPLEMENTATION_PLAN.md` - Phase 1

---

## Notes
- **CRITICAL SECURITY**: This validator is the primary enforcement mechanism for read-only operations
- Must be thoroughly tested with all edge cases
- Should be applied to ALL query execution endpoints
- Consider logging blocked queries for security auditing
- The validator is conservative - if in doubt, it should block
- Performance is important as this runs on every query
- Regex patterns are compiled once for efficiency
- The validator should never have false negatives (allowing write queries)
- False positives (blocking read queries) are acceptable if rare
- Consider adding metrics/monitoring for blocked queries in production
