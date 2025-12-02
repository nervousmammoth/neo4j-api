"""Unit tests for query execution endpoint.

This module tests the POST /api/{database}/graph/query endpoint following TDD principles.
"""

from __future__ import annotations

from unittest.mock import MagicMock, create_autospec

from fastapi import FastAPI
from fastapi.testclient import TestClient
from neo4j.exceptions import ClientError, Neo4jError
from neo4j.graph import Node as Neo4jNode
from neo4j.graph import Relationship as Neo4jRelationship

from app.config import Settings, get_settings
from app.routers.query import router


class TestQueryExecutionSuccess:
    """Test successful query execution scenarios."""

    def test_execute_read_query_returns_200(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that valid read query returns 200.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) RETURN n LIMIT 1"},
        )

        # Assert
        assert response.status_code == 200

    def test_execute_query_with_parameters(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query parameters are passed correctly.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={
                "query": "MATCH (p:Person) WHERE p.age > $age RETURN p",
                "parameters": {"age": 25},
            },
        )

        # Assert
        assert response.status_code == 200
        # Verify parameters were passed to execute_query
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        assert call_args.kwargs.get("parameters") == {"age": 25}

    def test_query_returns_nodes_in_linkurious_format(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query returns nodes in Linkurious format.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        # Create mock Neo4j node using create_autospec to pass isinstance checks
        mock_node = create_autospec(Neo4jNode, instance=True)
        mock_node.element_id = "4:abc:123"
        mock_node.labels = frozenset(["Person"])
        mock_node.items.return_value = [("name", "Alice"), ("age", 30)]

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [{"p": mock_node}]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (p:Person) RETURN p LIMIT 1"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert len(data["nodes"]) == 1
        node = data["nodes"][0]
        assert "id" in node
        assert "data" in node
        assert "categories" in node["data"]
        assert "properties" in node["data"]
        assert "Person" in node["data"]["categories"]
        assert node["data"]["properties"]["name"] == "Alice"

    def test_query_returns_edges_in_linkurious_format(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query returns edges in Linkurious format.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        # Create mock Neo4j nodes using create_autospec to pass isinstance checks
        mock_node1 = create_autospec(Neo4jNode, instance=True)
        mock_node1.element_id = "4:abc:1"
        mock_node1.labels = frozenset(["Person"])
        mock_node1.items.return_value = [("name", "Alice")]

        mock_node2 = create_autospec(Neo4jNode, instance=True)
        mock_node2.element_id = "4:abc:2"
        mock_node2.labels = frozenset(["Person"])
        mock_node2.items.return_value = [("name", "Bob")]

        # Create mock Neo4j relationship using create_autospec
        mock_rel = create_autospec(Neo4jRelationship, instance=True)
        mock_rel.element_id = "5:abc:100"
        mock_rel.type = "KNOWS"
        mock_rel.start_node = mock_node1
        mock_rel.end_node = mock_node2
        mock_rel.items.return_value = [("since", 2020)]

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"p": mock_node1, "r": mock_rel, "f": mock_node2}
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (p:Person)-[r:KNOWS]->(f:Person) RETURN p, r, f"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "edges" in data
        assert len(data["edges"]) == 1
        edge = data["edges"][0]
        assert "id" in edge
        assert "source" in edge
        assert "target" in edge
        assert "data" in edge
        assert "type" in edge["data"]
        assert edge["data"]["type"] == "KNOWS"

    def test_query_returns_execution_metadata(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query returns execution metadata.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) RETURN n LIMIT 1"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert data["meta"]["query_type"] == "r"
        assert "records_returned" in data["meta"]
        assert "execution_time_ms" in data["meta"]
        assert isinstance(data["meta"]["execution_time_ms"], int | float)

    def test_query_targets_specified_database(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query targets the database specified in path.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/testdb123/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) RETURN n"},
        )

        # Assert
        assert response.status_code == 200
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        assert call_args.kwargs.get("database") == "testdb123"

    def test_empty_results_return_valid_structure(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that empty results return valid structure with empty arrays.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n:NonExistent) RETURN n"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nodes"] == []
        assert data["edges"] == []
        assert data["truncatedByLimit"] is False


class TestQueryWriteBlocked:
    """Test that write operations are blocked (403)."""

    def test_create_query_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that CREATE query returns 403.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "CREATE (n:Person {name: 'Bob'}) RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "WRITE_OPERATION_FORBIDDEN"

    def test_delete_query_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that DELETE query returns 403.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) DELETE n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "WRITE_OPERATION_FORBIDDEN"

    def test_merge_query_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that MERGE query returns 403.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MERGE (n:Person {name: 'Bob'}) RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "WRITE_OPERATION_FORBIDDEN"

    def test_set_query_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that SET query returns 403.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) SET n.name = 'Alice' RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "WRITE_OPERATION_FORBIDDEN"

    def test_remove_query_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that REMOVE query returns 403.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) REMOVE n.name RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "WRITE_OPERATION_FORBIDDEN"

    def test_error_includes_forbidden_keyword(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that error includes forbidden keyword in details.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "CREATE (n:Person) RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert "details" in data["error"]
        assert "forbidden_keyword" in data["error"]["details"]
        assert data["error"]["details"]["forbidden_keyword"] == "CREATE"


class TestQueryAuthRequired:
    """Test that query endpoint requires authentication (403)."""

    def test_query_without_api_key_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that request without API key returns 403.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act - No X-API-Key header
        response = client.post(
            "/api/neo4j/graph/query",
            json={"query": "MATCH (n) RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        # HTTPException wraps detail in "detail" key
        assert data["detail"]["error"]["code"] == "MISSING_API_KEY"

    def test_query_with_invalid_api_key_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that request with invalid API key returns 403.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act - Invalid API key
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "wrong-api-key"},
            json={"query": "MATCH (n) RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        # HTTPException wraps detail in "detail" key
        assert data["detail"]["error"]["code"] == "INVALID_API_KEY"


class TestQuerySyntaxError:
    """Test query syntax error handling (400)."""

    def test_invalid_cypher_syntax_returns_400(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that invalid Cypher syntax returns 400.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.side_effect = Neo4jError(
            "Invalid input 'R': expected 'RETURN'"
        )
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n R n"},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "QUERY_SYNTAX_ERROR"


class TestQueryEdgeCases:
    """Test query edge cases."""

    def test_query_neo4j_unavailable_returns_503(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query returns 503 when Neo4j is unavailable.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        # Set client to None (simulating unavailable Neo4j)
        app.state.neo4j_client = None

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) RETURN n"},
        )

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "NEO4J_UNAVAILABLE"

    def test_query_with_empty_parameters(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query with empty parameters works.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) RETURN n", "parameters": {}},
        )

        # Assert
        assert response.status_code == 200

    def test_query_without_parameters_field(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query without parameters field works.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.return_value = []
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) RETURN n"},
        )

        # Assert
        assert response.status_code == 200
        # Verify empty parameters passed
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        assert call_args.kwargs.get("parameters") == {}


class TestQueryHelperFunctions:
    """Test internal helper functions for coverage."""

    def test_truncate_query_short_query(self) -> None:
        """Test that short queries are not truncated."""
        from app.routers.query import _truncate_query

        result = _truncate_query("MATCH (n) RETURN n")
        assert result == "MATCH (n) RETURN n"

    def test_truncate_query_long_query(self) -> None:
        """Test that long queries are truncated."""
        from app.routers.query import _truncate_query

        long_query = "MATCH (n) " * 20  # 200 chars
        result = _truncate_query(long_query)
        assert len(result) < len(long_query)
        assert result.endswith("... [truncated]")

    def test_extract_error_position_with_column(self) -> None:
        """Test that position is extracted from column info."""
        from app.routers.query import _extract_error_position

        error_msg = "Invalid input 'X' (line 1, column 10)"
        result = _extract_error_position(error_msg)
        assert result == 10

    def test_extract_error_position_with_position(self) -> None:
        """Test that position is extracted from position info."""
        from app.routers.query import _extract_error_position

        error_msg = "Syntax error at position 25"
        result = _extract_error_position(error_msg)
        assert result == 25

    def test_extract_error_position_no_position(self) -> None:
        """Test that None is returned when no position info."""
        from app.routers.query import _extract_error_position

        error_msg = "Unknown error occurred"
        result = _extract_error_position(error_msg)
        assert result is None

    def test_extract_graph_elements_handles_nested_lists(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that nested lists in query results are processed.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        # Create mock Neo4j node inside a list
        mock_node = create_autospec(Neo4jNode, instance=True)
        mock_node.element_id = "4:abc:123"
        mock_node.labels = frozenset(["Person"])
        mock_node.items.return_value = [("name", "Alice")]

        mock_client = MagicMock()
        # Return a list of nodes inside the result
        mock_client.execute_query.return_value = [{"nodes": [mock_node]}]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (p:Person) RETURN collect(p) as nodes"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 1

    def test_extract_graph_elements_handles_nested_dicts(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that nested dicts in query results are processed.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        # Create mock Neo4j node inside a dict
        mock_node = create_autospec(Neo4jNode, instance=True)
        mock_node.element_id = "4:abc:123"
        mock_node.labels = frozenset(["Person"])
        mock_node.items.return_value = [("name", "Alice")]

        mock_client = MagicMock()
        # Return a dict containing a node
        mock_client.execute_query.return_value = [{"result": {"person": mock_node}}]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (p:Person) RETURN {person: p} as result"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 1

    def test_relationship_with_null_nodes_handled(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that relationships with null start/end nodes are handled.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        # Create mock relationship with None nodes
        mock_rel = create_autospec(Neo4jRelationship, instance=True)
        mock_rel.element_id = "5:abc:100"
        mock_rel.type = "KNOWS"
        mock_rel.start_node = None  # Null start node
        mock_rel.end_node = None  # Null end node
        mock_rel.items.return_value = []

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [{"r": mock_rel}]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH ()-[r]->() RETURN r"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Relationship should be skipped because nodes are None
        assert len(data["edges"]) == 0
        assert len(data["nodes"]) == 0

    def test_relationship_with_partial_null_nodes(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test relationship with one null node is handled correctly.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        # Create valid node
        mock_node = create_autospec(Neo4jNode, instance=True)
        mock_node.element_id = "4:abc:1"
        mock_node.labels = frozenset(["Person"])
        mock_node.items.return_value = [("name", "Alice")]

        # Create relationship with only start_node
        mock_rel = create_autospec(Neo4jRelationship, instance=True)
        mock_rel.element_id = "5:abc:100"
        mock_rel.type = "KNOWS"
        mock_rel.start_node = mock_node
        mock_rel.end_node = None  # Null end node
        mock_rel.items.return_value = []

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [{"r": mock_rel}]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH ()-[r]->() RETURN r"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Edge skipped but start_node extracted
        assert len(data["edges"]) == 0
        assert len(data["nodes"]) == 1

    def test_extract_graph_elements_handles_scalar_values(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that scalar values (non-node/edge) are handled correctly.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        from app.routers.query import router

        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        # Return results with only scalar values (no nodes/edges)
        mock_client.execute_query.return_value = [
            {"count": 42, "name": "test", "data": {"nested": "value"}}
        ]
        app.state.neo4j_client = mock_client

        from app.config import get_settings

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (p:Person) RETURN count(p) as count"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # No nodes or edges extracted from scalar values
        assert len(data["nodes"]) == 0
        assert len(data["edges"]) == 0


class TestQueryResponseEnhancements:
    """Test new response enhancements from PR review fixes."""

    def test_403_includes_allowed_operations(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that 403 response includes allowed_operations list.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "CREATE (n:Person) RETURN n"},
        )

        # Assert
        assert response.status_code == 403
        error = response.json()["error"]
        assert "allowed_operations" in error["details"]
        assert "MATCH" in error["details"]["allowed_operations"]
        assert "RETURN" in error["details"]["allowed_operations"]

    def test_403_includes_detach_delete_keyword(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that DETACH DELETE is correctly identified.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) DETACH DELETE n"},
        )

        # Assert
        assert response.status_code == 403
        error = response.json()["error"]
        assert error["details"]["forbidden_keyword"] == "DETACH DELETE"

    def test_400_includes_position_when_available(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that syntax error includes position when available.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.side_effect = Neo4jError(
            "Invalid input 'X' (line 1, column 10)"
        )
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH X RETURN n"},
        )

        # Assert
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["details"]["position"] == 10

    def test_error_responses_truncate_long_queries(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that long queries are truncated in error responses.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Create a long query (>100 chars)
        long_query = "CREATE (n:Person {name: '" + "A" * 150 + "'}) RETURN n"

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": long_query},
        )

        # Assert
        assert response.status_code == 403
        error = response.json()["error"]
        query_in_response = error["details"]["query"]
        assert len(query_in_response) < len(long_query)
        assert query_in_response.endswith("... [truncated]")

    def test_query_timeout_returns_504(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that query timeout returns 504.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        mock_client.execute_query.side_effect = ClientError("Query execution timed out")
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n)-[*10..20]-(m) RETURN n, m"},
        )

        # Assert
        assert response.status_code == 504
        error = response.json()["error"]
        assert error["code"] == "QUERY_TIMEOUT"
        assert "timeout_seconds" in error["details"]

    def test_non_timeout_client_error_raises(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that non-timeout ClientError is re-raised and caught as Neo4jError.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        # ClientError that is not about timeout - will be re-raised
        mock_client.execute_query.side_effect = ClientError("Some other client error")
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app, raise_server_exceptions=False)

        # Act
        response = client.post(
            "/api/neo4j/graph/query",
            headers={"X-API-Key": "test-api-key-12345"},
            json={"query": "MATCH (n) RETURN n"},
        )

        # Assert - should get 500 as ClientError is re-raised
        assert response.status_code == 500
