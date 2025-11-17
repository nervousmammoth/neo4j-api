# Issue 05: Implement Neo4j Client Wrapper

## Status
⏳ **TODO**

**Estimated Time:** 3 hours
**Branch:** `issue/05-neo4j-client`
**Phase:** 1 - Core Infrastructure

## Description
Implement `app/utils/neo4j_client.py` as a wrapper around the Neo4j Python driver with multi-database support, connection pooling, and proper error handling. This is a critical component used by all database-interacting endpoints.

## Related Specifications
- [ ] **Spec file:** `specs/api-overview.md` - Section 3 (Architecture)
- [ ] **Spec file:** `specs/error-handling.md` - Database connection errors
- [ ] **Reference:** Neo4j Python Driver documentation

## Related BDD Tests
- [ ] **Feature file:** `features/health.feature` - Database connectivity tests
- [ ] **Scenarios:** "Database is connected", "Database connection fails"

## Dependencies
- [ ] Issue #04 - Config module must be implemented first

---

## TDD Workflow Checklist

### 1️⃣ RED - Write Failing Tests
- [ ] Create test file: `tests/test_neo4j_client.py`
- [ ] Write unit tests for Neo4jClient class
  - [ ] Test client initialization with settings
  - [ ] Test verify_connectivity() method
  - [ ] Test execute_query() method
  - [ ] Test execute_query() with specific database
  - [ ] Test connection error handling
  - [ ] Test query execution error handling
  - [ ] Test session management
  - [ ] Test close() method
- [ ] Run tests: `pytest tests/test_neo4j_client.py -v`
- [ ] **Verify tests FAIL** ❌

### 2️⃣ GREEN - Implement Minimum Code
- [ ] Create implementation file: `app/utils/neo4j_client.py`
- [ ] Implement Neo4jClient class
  - [ ] __init__() method with driver creation
  - [ ] verify_connectivity() method
  - [ ] execute_query() method with database parameter
  - [ ] close() method
  - [ ] Context manager support (__enter__, __exit__)
  - [ ] Error handling and logging
- [ ] Run tests: `pytest tests/test_neo4j_client.py -v`
- [ ] **Verify tests PASS** ✅

### 3️⃣ REFACTOR - Improve Code Quality
- [ ] Run black: `black app/ tests/`
- [ ] Run ruff: `ruff check app/ tests/ --fix`
- [ ] Run mypy: `mypy app/`
- [ ] **Verify tests still pass** ✅

### 4️⃣ BDD Validation (if applicable)
- [ ] Run related BDD scenarios: `behave features/health.feature -v`
- [ ] **Verify BDD scenarios pass** ✅

### 5️⃣ Coverage Check
- [ ] Run coverage: `pytest --cov=app.utils.neo4j_client --cov-report=term-missing --cov-report=html`
- [ ] **Verify 100% coverage** for new code ✅
- [ ] Check HTML report: `open htmlcov/index.html`

---

## Acceptance Criteria

### Functional Requirements
- [ ] Neo4jClient class wraps Neo4j driver
- [ ] Supports multi-database connections via database parameter
- [ ] Connection pooling configured from settings
- [ ] verify_connectivity() tests database connection
- [ ] execute_query() executes Cypher queries
- [ ] execute_query() supports parameterized queries
- [ ] execute_query() accepts database name parameter
- [ ] Proper error handling for connection failures
- [ ] Proper error handling for query execution failures
- [ ] Context manager support for resource cleanup
- [ ] Logging for connection events and errors

### Non-Functional Requirements
- [ ] Unit tests written (TDD approach)
- [ ] 100% code coverage for new code
- [ ] Type hints present (mypy compliant)
- [ ] Code formatted (black)
- [ ] Linting passed (ruff)
- [ ] No security issues (bandit)
- [ ] BDD scenarios pass
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
app/utils/neo4j_client.py
tests/test_neo4j_client.py
```

### Key Implementation Details

**Neo4jClient class responsibilities:**
- Wrap Neo4j driver creation and management
- Support multi-database operations
- Handle connection pooling configuration
- Provide clean interface for query execution
- Manage session lifecycle
- Handle errors gracefully
- Support context manager protocol

**Query execution:**
- Accept Cypher query string
- Accept query parameters dictionary
- Accept database name (for multi-database support)
- Return query results as list of records
- Raise appropriate exceptions on errors

**Connection management:**
- Create driver on initialization
- Verify connectivity with verify_connectivity()
- Close driver properly on shutdown
- Support context manager for automatic cleanup

### Example Code Structure

```python
"""Neo4j database client wrapper.

This module provides a wrapper around the Neo4j Python driver with
multi-database support and connection pooling.
"""

from __future__ import annotations

import logging
from typing import Any

from neo4j import Driver, GraphDatabase, Session
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.config import Settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j database client with multi-database support.

    This class wraps the Neo4j Python driver and provides a clean interface
    for executing queries across multiple databases.

    Attributes:
        driver: Neo4j driver instance.
        settings: Application settings.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize Neo4j client with settings.

        Args:
            settings: Application settings containing Neo4j configuration.

        Raises:
            ServiceUnavailable: If connection cannot be established.
        """
        self.settings = settings
        self.driver: Driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password.get_secret_value()),
            max_connection_lifetime=settings.neo4j_max_connection_lifetime,
            max_connection_pool_size=settings.neo4j_max_connection_pool_size,
            connection_timeout=settings.neo4j_connection_timeout,
        )
        logger.info("Neo4j driver initialized for %s", settings.neo4j_uri)

    def verify_connectivity(self) -> bool:
        """Verify Neo4j database connectivity.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            self.driver.verify_connectivity()
            logger.info("Neo4j connectivity verified")
            return True
        except ServiceUnavailable as e:
            logger.error("Neo4j service unavailable: %s", e)
            return False
        except Neo4jError as e:
            logger.error("Neo4j connectivity error: %s", e)
            return False

    def execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        database: str | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query.

        Args:
            query: Cypher query string.
            parameters: Query parameters (optional).
            database: Database name (optional, uses default if not specified).

        Returns:
            List of result records as dictionaries.

        Raises:
            Neo4jError: If query execution fails.
        """
        db = database or self.settings.neo4j_database
        params = parameters or {}

        try:
            with self.driver.session(database=db) as session:
                result = session.run(query, params)
                records = [record.data() for record in result]
                logger.debug(
                    "Executed query on database '%s', returned %d records",
                    db,
                    len(records),
                )
                return records
        except Neo4jError as e:
            logger.error("Query execution error on database '%s': %s", db, e)
            raise

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed")

    def __enter__(self) -> Neo4jClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.close()
```

### Testing Strategy

**Unit tests:**
- Mock `GraphDatabase.driver` to avoid real Neo4j connection
- Test driver initialization with correct parameters
- Test verify_connectivity() returns True on success
- Test verify_connectivity() returns False on ServiceUnavailable
- Test execute_query() with basic query
- Test execute_query() with parameters
- Test execute_query() with specific database
- Test execute_query() raises Neo4jError on failure
- Test close() calls driver.close()
- Test context manager calls close() on exit

**Mocking approach:**
- Use `@patch('app.utils.neo4j_client.GraphDatabase.driver')`
- Mock driver, session, and result objects
- Use mock_neo4j_driver and mock_neo4j_session fixtures from conftest.py
- Simulate connection failures with side_effect
- Simulate query failures with exceptions

**Edge cases:**
- Connection timeout
- Authentication failure
- Invalid database name
- Query syntax errors
- Connection lost during query
- Empty result sets
- Large result sets

---

## Git Workflow

### Start Issue
```bash
git checkout main
git pull origin main
git checkout -b issue/05-neo4j-client
```

### During Development
```bash
# TDD Cycle: Write tests first
# Create tests/test_neo4j_client.py with comprehensive tests
# Run pytest tests/test_neo4j_client.py -v (should FAIL)

# Implement app/utils/neo4j_client.py
# Run pytest tests/test_neo4j_client.py -v (should PASS)

# Refactor
black app/ tests/
ruff check app/ tests/ --fix
mypy app/

# Verify coverage
pytest tests/test_neo4j_client.py --cov=app.utils.neo4j_client --cov-report=term-missing

# Run related BDD tests
behave features/health.feature -v

# Commit
git add app/utils/neo4j_client.py tests/test_neo4j_client.py
git commit -m "feat(issue-05): implement Neo4j client wrapper with multi-database support"

# Push
git push origin issue/05-neo4j-client
```

### Create Pull Request
```bash
gh pr create \
  --title "feat: implement Neo4j client wrapper" \
  --body "$(cat <<'EOF'
## Summary
- Implemented Neo4j client wrapper with multi-database support
- Added connection pooling and error handling
- Comprehensive unit tests with 100% coverage

## Changes
- Created Neo4jClient class wrapping Neo4j driver
- Implemented verify_connectivity() for health checks
- Implemented execute_query() with multi-database support
- Added context manager support for resource cleanup
- Full error handling and logging
- Complete test coverage with mocked driver

## Testing
- [x] Unit tests pass (pytest)
- [x] BDD tests pass (behave)
- [x] 100% coverage achieved
- [x] Pre-commit hooks pass

## Closes
Closes #05

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### After Merge
```bash
mv issues/05-neo4j-client.md issues/completed/
git checkout main
git pull origin main
```

---

## Verification Commands

```bash
# Run unit tests
pytest tests/test_neo4j_client.py -v

# Run with coverage
pytest tests/test_neo4j_client.py --cov=app.utils.neo4j_client --cov-report=term-missing

# Run BDD scenarios
behave features/health.feature -v

# Run type checking
mypy app/utils/neo4j_client.py

# Run all quality checks
pre-commit run --all-files
```

---

## References
- **Neo4j Python Driver:** https://neo4j.com/docs/api/python-driver/current/
- **Specification:** `specs/api-overview.md`
- **BDD Feature:** `features/health.feature`
- **Implementation Plan:** `IMPLEMENTATION_PLAN.md` - Phase 1

---

## Notes
- Always mock GraphDatabase.driver in unit tests (use @patch)
- The client should be created once and reused (singleton pattern via FastAPI dependency)
- Connection pooling is handled by the Neo4j driver internally
- Session management is automatic using context manager
- This client will be injected as a dependency in all endpoint routers
- Multi-database support is critical for Linkurious compatibility
- Proper logging helps with debugging connection issues in production
