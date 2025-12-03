# Test Fixtures

This directory will contain test data fixtures for unit and integration tests.

## Planned Structure

```
fixtures/
├── README.md       # This file
├── requests/       # Sample API request payloads
├── responses/      # Expected API response payloads
└── data/           # Test data (nodes, relationships)
```

## Status

**Not yet implemented.** Fixture subdirectories and files will be created as needed during test development.

## Usage

Fixtures can be loaded in tests:

```python
import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def load_fixture(filename: str) -> dict:
    """Load a JSON fixture file."""
    fixture_path = FIXTURES_DIR / filename
    with open(fixture_path, "r") as f:
        return json.load(f)
```

## Example

```python
# In a pytest test
def test_health_response_format():
    expected = load_fixture("responses/health_healthy.json")
    response = client.get("/api/health")
    assert response.json() == expected
```

## Planned Fixtures

Once implemented, this directory will contain:

- `data/sample_nodes.json` - Sample node data for testing
- `responses/health_healthy.json` - Healthy health check response
- `responses/error_responses.json` - Standard error response formats
- `requests/query_example.json` - Example Cypher query request

## Adding New Fixtures

1. Create the appropriate subdirectory if it doesn't exist (`requests/`, `responses/`, or `data/`)
2. Create JSON file following the response format from `specs/examples/`
3. Update this README with the new fixture
