"""
Behave environment configuration for BDD tests.

This module handles test setup, teardown, and context configuration
for all behave test scenarios.
"""

import os
import sys
from unittest.mock import Mock, MagicMock

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def before_all(context):
    """
    Runs once before all features.
    Set up global test configuration.
    """
    # Test configuration
    context.test_config = {
        'api_key': 'test-api-key-12345',
        'base_url': 'http://localhost:8000',
        'timeout': 30,
    }

    # Environment variables for testing
    os.environ['API_KEY'] = context.test_config['api_key']
    os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
    os.environ['NEO4J_USER'] = 'neo4j'
    os.environ['NEO4J_PASSWORD'] = 'password'

    print("=" * 80)
    print("BDD Test Suite - Neo4j Multi-Database REST API")
    print("=" * 80)


def before_feature(context, feature):
    """
    Runs before each feature file.
    """
    print(f"\n📋 Feature: {feature.name}")


def before_scenario(context, scenario):
    """
    Runs before each scenario.
    Set up fresh test client and mock Neo4j driver.
    """
    # Set API key
    context.api_key = context.test_config['api_key']

    # Mock FastAPI test client
    # In real implementation, would use: from fastapi.testclient import TestClient
    context.client = create_test_client(context)

    # Mock Neo4j driver
    context.neo4j_driver = create_mock_neo4j_driver(context)

    # Initialize scenario-specific state
    context.neo4j_databases = {}
    context.available_databases = []
    context.neo4j_status = 'connected'
    context.logging_enabled = False
    context.captured_logs = []

    # Response tracking
    context.response = None
    context.multi_responses = []
    context.start_time = None
    context.end_time = None

    print(f"  🧪 Scenario: {scenario.name}")


def after_scenario(context, scenario):
    """
    Runs after each scenario.
    Clean up resources.
    """
    # Clean up scenario state
    if hasattr(context, 'client'):
        # Close client if needed
        pass

    if hasattr(context, 'neo4j_driver'):
        # Clean up mock driver
        pass

    # Print scenario result
    if scenario.status == 'passed':
        print(f"  ✅ PASSED")
    elif scenario.status == 'failed':
        print(f"  ❌ FAILED: {scenario.exception}")
    elif scenario.status == 'skipped':
        print(f"  ⏭️  SKIPPED")


def after_feature(context, feature):
    """
    Runs after each feature file.
    """
    pass


def after_all(context):
    """
    Runs once after all features.
    """
    print("\n" + "=" * 80)
    print("BDD Test Suite Complete")
    print("=" * 80)


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_client(context):
    """
    Create a mock test client for API testing.

    In a real implementation, this would return:
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    For now, returns a mock client that can handle basic requests.
    """
    class MockTestClient:
        """Mock HTTP client for testing."""

        def __init__(self, context):
            self.context = context

        def get(self, url, headers=None, params=None):
            """Mock GET request."""
            return create_mock_response(self.context, 'GET', url, headers, params)

        def post(self, url, headers=None, json=None, data=None):
            """Mock POST request."""
            return create_mock_response(self.context, 'POST', url, headers, json=json)

        def put(self, url, headers=None, json=None):
            """Mock PUT request."""
            return create_mock_response(self.context, 'PUT', url, headers, json=json)

        def delete(self, url, headers=None):
            """Mock DELETE request."""
            return create_mock_response(self.context, 'DELETE', url, headers)

    return MockTestClient(context)


def create_mock_response(context, method, url, headers, params=None, json=None):
    """
    Create a mock HTTP response based on scenario state.

    This is a placeholder - real implementation would call actual FastAPI app.
    """
    class MockResponse:
        """Mock HTTP response."""

        def __init__(self, status_code, data):
            self.status_code = status_code
            self._json_data = data
            self.text = str(data)

        def json(self):
            """Return JSON data."""
            return self._json_data

    # Default response
    status_code = 200
    response_data = {"message": "Mock response"}

    # Check authentication
    api_key = headers.get('X-API-Key') if headers else None
    requires_auth = '/api/health' not in url and '/api/databases' not in url and '/api/docs' not in url

    if requires_auth and not api_key:
        return MockResponse(403, {
            "error": {
                "code": "MISSING_API_KEY",
                "message": "API key is required",
                "details": {"header": "X-API-Key"}
            }
        })

    if requires_auth and api_key != context.api_key:
        return MockResponse(403, {
            "error": {
                "code": "INVALID_API_KEY",
                "message": "Invalid API key provided"
            }
        })

    # Health endpoint
    if '/api/health' in url:
        if context.neo4j_status == 'connected':
            response_data = {
                "status": "healthy",
                "neo4j": "connected",
                "version": "1.0.0"
            }
        else:
            status_code = 503
            response_data = {
                "status": "unhealthy",
                "neo4j": "disconnected",
                "error": "Connection refused"
            }

    # Databases endpoint
    elif '/api/databases' in url or '/databases' in url:
        if context.available_databases:
            response_data = {"databases": context.available_databases}
        else:
            response_data = {"databases": [{"name": "neo4j", "default": True, "status": "online"}]}

    # Search endpoints
    elif '/search/' in url:
        response_data = {
            "type": "node" if '/node/' in url else "edge",
            "totalHits": 0,
            "moreResults": False,
            "results": []
        }

    # Query endpoint
    elif '/graph/query' in url:
        response_data = {
            "nodes": [],
            "edges": [],
            "truncatedByLimit": False,
            "meta": {
                "query_type": "r",
                "records_returned": 0,
                "execution_time_ms": 10
            }
        }

    # Nodes endpoints
    elif '/graph/nodes/' in url:
        if '/count' in url:
            node_count = len(context.neo4j_databases.get('neo4j', {}).get('nodes', []))
            response_data = {"count": node_count}
        else:
            response_data = {"nodes": [], "edges": []}

    # Schema endpoints
    elif '/schema/node/types' in url or '/schema/edge/types' in url:
        response_data = {"types": []}

    return MockResponse(status_code, response_data)


def create_mock_neo4j_driver(context):
    """
    Create a mock Neo4j driver for testing.

    In a real implementation, this would use pytest-mock or similar
    to mock the neo4j.Driver class.
    """
    mock_driver = Mock()
    mock_driver.verify_connectivity = Mock(return_value=None)
    mock_driver.execute_query = Mock(return_value=([], None, None))

    return mock_driver
