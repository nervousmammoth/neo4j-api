# Test Fixtures

This directory contains test data fixtures used in BDD tests.

## Structure

```
fixtures/
├── requests/       # Sample API request payloads
├── responses/      # Expected API response payloads
└── data/           # Test data (nodes, relationships)
```

## Usage

Fixtures can be loaded in step definitions:

```python
import json
from pathlib import Path

def load_fixture(filename):
    fixture_path = Path(__file__).parent.parent.parent / 'fixtures' / filename
    with open(fixture_path, 'r') as f:
        return json.load(f)
```

## Example

```python
# In step definition
@given('the database contains sample data')
def step_load_sample_data(context):
    data = load_fixture('data/sample_nodes.json')
    # Use data to mock Neo4j responses
```

## Available Fixtures

- `data/sample_nodes.json` - Sample node data for testing
- `responses/health_healthy.json` - Healthy health check response
- `responses/error_missing_api_key.json` - Missing API key error response
- `requests/query_example.json` - Example Cypher query request

## Adding New Fixtures

1. Create JSON file in appropriate subdirectory
2. Follow the response format from specs/examples/
3. Document the fixture purpose in this README
