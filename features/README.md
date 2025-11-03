# BDD Feature Tests

This directory contains Behavior-Driven Development (BDD) tests written in Gherkin using the **behave** framework.

## Overview

BDD tests serve as **executable specifications** that validate the API behaves according to the requirements defined in `specs/`. These tests complement unit tests by:

- Testing the API at the **acceptance level** (end-to-end behavior)
- Providing **living documentation** readable by non-technical stakeholders
- Validating **business requirements** rather than implementation details
- Ensuring specifications and implementation stay **synchronized**

## Directory Structure

```
features/
├── README.md                     # This file
├── environment.py                # Test setup/teardown hooks
├── behave.ini                    # Behave configuration (at project root)
│
├── health.feature                # Health & metadata endpoint tests
├── authentication.feature        # API key authentication tests
├── search.feature                # Search endpoint tests
├── query.feature                 # Cypher query execution tests
├── nodes.feature                 # Node operation tests
├── schema.feature                # Schema discovery tests
│
└── steps/                        # Step definitions (test implementation)
    ├── http_steps.py             # HTTP request/response steps
    ├── common_steps.py           # Common reusable steps
    ├── auth_steps.py             # Authentication-specific steps
    └── neo4j_steps.py            # Neo4j database-specific steps
```

## Running BDD Tests

### Quick Start

```bash
# Run all tests
./scripts/run_bdd_tests.sh

# Run smoke tests only (fastest)
./scripts/run_bdd_tests.sh --smoke

# Run specific feature
behave features/health.feature

# Run tests by tag
behave features/ --tags=@auth
behave features/ --tags=@critical
behave features/ --tags="@smoke and @health"
behave features/ --tags="@search or @query"
behave features/ --tags="not @wip"  # Exclude work-in-progress
```

### Common Options

```bash
# Verbose output
behave features/ -v

# Stop on first failure
behave features/ --stop

# Dry run (validate Gherkin syntax)
behave features/ --dry-run

# Generate HTML report
behave features/ --format=html --outfile=reports/behave/index.html

# Show only scenarios (no steps)
behave features/ --no-capture --format=progress

# Capture stdout/stderr
behave features/ --no-capture
```

## Feature Files

### Gherkin Syntax

Feature files use Gherkin syntax with Given-When-Then structure:

```gherkin
Feature: Short description of feature
  As a [role]
  I want [feature]
  So that [benefit]

  Background:
    Given common setup for all scenarios

  @tag1 @tag2
  Scenario: Description of test scenario
    Given initial context
    When action occurs
    Then expected outcome
    And additional assertion
```

### Available Features

| Feature File | Description | Key Scenarios |
|--------------|-------------|---------------|
| `health.feature` | Health checks and database listing | API health, database discovery |
| `authentication.feature` | API key authentication | Valid/invalid keys, public endpoints |
| `search.feature` | Node and edge search | Fuzzy search, pagination, filters |
| `query.feature` | Cypher query execution | Read-only enforcement, parameters |
| `nodes.feature` | Node operations | Get by ID, expand, count |
| `schema.feature` | Schema discovery | Labels, relationship types |

## Test Tags

Tags allow selective test execution:

### By Priority
- `@smoke` - Critical smoke tests (15-20 tests, < 1 min)
- `@critical` - High-priority tests
- `@integration` - Integration tests (slower)

### By Feature Area
- `@health` - Health & metadata
- `@auth` - Authentication
- `@search` - Search functionality
- `@query` - Query execution
- `@nodes` - Node operations
- `@schema` - Schema discovery

### By Type
- `@error` - Error handling tests
- `@validation` - Input validation
- `@security` - Security tests
- `@performance` - Performance tests
- `@format` - Response format tests
- `@database` - Multi-database tests

### By Status
- `@wip` - Work in progress (excluded by default)
- `@manual` - Manual testing required
- `@skip` - Temporarily disabled

## Step Definitions

### http_steps.py

Common HTTP request/response steps:

```gherkin
# Requests
When I send a GET request to "/api/endpoint"
When I send a POST request to "/api/endpoint" with authentication
When I send a GET request to "/api/endpoint" with headers:
  | header    | value |
  | X-API-Key | test  |

# Response status
Then the response status code should be 200
Then the response status code should not be 403

# Response time
Then the response time should be less than 1000 milliseconds

# JSON validation
Then the JSON response should have field "status" with value "healthy"
Then the JSON response should have a "results" array
Then the response should contain 5 results

# Error validation
Then the error code should be "MISSING_API_KEY"
Then the error message should contain "required"
Then the error details should have field "database" with value "neo4j"
```

### common_steps.py

General-purpose steps:

```gherkin
# Setup
Given the API is running
Given I have a valid API key

# Array validation
Then the "results" array should contain 10 items
Then the "results" array should be empty
Then the "types" array should contain "Person"
Then the "types" array should be sorted alphabetically

# Field validation
Then the first result should have property "name" with value "Alice"
Then the database "neo4j" should be marked as default
```

### auth_steps.py

Authentication-specific steps:

```gherkin
Given the configured API key is "test-api-key"
Given I have a valid API key "my-key"
When I send authenticated requests to the following endpoints:
  | method | endpoint              |
  | GET    | /api/neo4j/search/... |
Then all requests should return status code 200 or 400
```

### neo4j_steps.py

Neo4j database state and operations:

```gherkin
# Database state
Given the Neo4j database is connected
Given the Neo4j database is disconnected
Given the database is empty
Given the database contains 100 nodes

# Database content
Given the database contains nodes with labels:
  | label   |
  | Person  |
  | Company |
Given the database contains a node with ID "123"

# Search
When I search for nodes with query "Alice"
When I search for nodes with query "Alice" and fuzziness 0.8
When I search for edges with query "WORKS_FOR"

# Query execution
When I execute the Cypher query:
  """
  MATCH (n:Person) RETURN n LIMIT 10
  """
When I execute the Cypher query with parameters:
  """
  MATCH (n:Person) WHERE n.age > $age RETURN n
  """
  | parameter | value |
  | age       | 25    |
```

## Writing New Tests

### 1. Create Feature File

```gherkin
# features/my_feature.feature
Feature: My New Feature
  As an API user
  I want to perform some action
  So that I can achieve a goal

  Background:
    Given the API is running
    And I have a valid API key

  @smoke @my_feature
  Scenario: Basic functionality works
    Given some initial state
    When I perform an action
    Then I should see expected result
```

### 2. Run Test (Will Fail)

```bash
behave features/my_feature.feature
# Shows which steps are undefined
```

### 3. Implement Missing Steps

If you need custom steps not in existing step files:

```python
# features/steps/my_feature_steps.py
from behave import given, when, then

@given('some initial state')
def step_setup_state(context):
    # Implementation
    pass

@when('I perform an action')
def step_perform_action(context):
    # Implementation
    pass

@then('I should see expected result')
def step_verify_result(context):
    # Assertion
    assert context.response.status_code == 200
```

### 4. Run Again (Should Pass)

```bash
behave features/my_feature.feature -v
```

## Best Practices

### Feature Files

✅ **Do:**
- Write scenarios from user perspective
- Use descriptive scenario names
- Keep scenarios focused (test one thing)
- Use Background for common setup
- Add appropriate tags
- Include tables for test data
- Write in present tense

❌ **Don't:**
- Test implementation details
- Write overly long scenarios (> 10 steps)
- Duplicate scenarios across features
- Use technical jargon users won't understand
- Mix concerns in a single scenario

### Step Definitions

✅ **Do:**
- Reuse existing steps when possible
- Keep steps simple and focused
- Add clear assertions with helpful error messages
- Handle edge cases gracefully
- Use context to share state between steps

❌ **Don't:**
- Put business logic in step definitions
- Duplicate step implementations
- Use hard-coded values (use parameters)
- Make steps too generic or too specific

## Debugging Tests

### Show Step Output

```bash
behave features/ --no-capture
```

### Print Context Variables

```python
# In step definition
print(f"Response: {context.response.json()}")
print(f"Status: {context.response.status_code}")
```

### Run Single Scenario by Line Number

```bash
behave features/health.feature:15
```

### Enable Verbose Logging

```bash
behave features/ -v --logging-level=DEBUG
```

## Continuous Integration

Tests run automatically in GitHub Actions:

1. **Smoke Tests** - Run first for fast feedback
2. **All BDD Tests** - Full suite
3. **HTML Report** - Generated as artifact

See `.github/workflows/test.yml` for details.

## Coverage and Reporting

### HTML Reports

After running tests with `./scripts/run_bdd_tests.sh`:

```bash
# View HTML report
open reports/behave/index.html
```

### JSON Results

```bash
# Parse JSON results
cat reports/behave/results.json | jq '.[] | select(.status == "failed")'
```

### Integration with Specs

BDD tests validate behavior specified in `specs/`:

- `specs/endpoints-health.md` → `features/health.feature`
- `specs/endpoints-search.md` → `features/search.feature`
- `specs/endpoints-query.md` → `features/query.feature`
- etc.

## Troubleshooting

### Tests Fail with "Step not implemented"

Add missing step definition in appropriate `steps/*.py` file.

### Tests Pass but Shouldn't

Check mock responses in `environment.py` - they may need updating.

### Import Errors

Ensure virtual environment is activated and dependencies installed:

```bash
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Behave Not Found

```bash
pip install behave behave-html-formatter
```

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
- [BDD Best Practices](https://cucumber.io/docs/bdd/)
- [Writing Good Gherkin](https://cucumber.io/docs/gherkin/reference/)

---

**Remember:** BDD tests are documentation that executes. Write them so non-technical stakeholders can understand the API's behavior!
