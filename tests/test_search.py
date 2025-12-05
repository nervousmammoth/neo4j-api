"""Unit tests for search endpoints.

This module tests the GET /api/{database}/search/node/full endpoint following TDD principles.
"""

from __future__ import annotations

from unittest.mock import MagicMock, create_autospec

from fastapi import FastAPI
from fastapi.testclient import TestClient
from neo4j.exceptions import ClientError
from neo4j.graph import Node as Neo4jNode
from neo4j.graph import Relationship as Neo4jRelationship

from app.config import Settings, get_settings
from app.routers.search import router


class TestNodeSearchSuccess:
    """Test successful node search scenarios."""

    def test_search_nodes_returns_200_with_results(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that valid search query returns 200 with results.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_node = create_autospec(Neo4jNode, instance=True)
        mock_node.element_id = "4:abc:123"
        mock_node.labels = frozenset(["Person"])
        mock_node.items.return_value = [("name", "Alice"), ("age", 30)]

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [{"n": mock_node}]
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/neo4j/search/node/full?q=Alice",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "node"
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == "4:abc:123"
        assert data["results"][0]["labels"] == ["Person"]
        assert data["results"][0]["properties"]["name"] == "Alice"

    def test_search_nodes_returns_empty_results(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that search with no matches returns empty results.

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
        response = client.get(
            "/api/neo4j/search/node/full?q=NonexistentPerson",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "node"
        assert data["totalHits"] == 0
        assert data["results"] == []

    def test_search_nodes_pagination_with_size_and_from(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that pagination parameters are passed correctly.

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
        response = client.get(
            "/api/neo4j/search/node/full?q=test&size=50&from=100",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        # Verify parameters were passed to execute_query
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        params = call_args.kwargs.get("parameters", {})
        assert params.get("size") == 50
        assert params.get("from_param") == 100

    def test_search_nodes_response_format_matches_spec(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that response format matches Linkurious spec.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_node = create_autospec(Neo4jNode, instance=True)
        mock_node.element_id = "4:abc:456"
        mock_node.labels = frozenset(["Person", "Employee"])
        mock_node.items.return_value = [("name", "Bob"), ("department", "Engineering")]

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [{"n": mock_node}]
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/neo4j/search/node/full?q=Bob",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Check response structure
        assert "type" in data
        assert "totalHits" in data
        assert "moreResults" in data
        assert "results" in data
        # Check result structure
        result = data["results"][0]
        assert "id" in result
        assert "labels" in result
        assert "properties" in result
        # Verify camelCase serialization
        assert "totalHits" in data
        assert "moreResults" in data

    def test_search_nodes_case_insensitive(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that search is case insensitive.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_node = create_autospec(Neo4jNode, instance=True)
        mock_node.element_id = "4:abc:789"
        mock_node.labels = frozenset(["Person"])
        mock_node.items.return_value = [("name", "ALICE")]

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [{"n": mock_node}]
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act - search with lowercase
        response = client.get(
            "/api/neo4j/search/node/full?q=alice",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        # Verify the query uses case-insensitive matching
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        query = call_args.kwargs.get("query", "")
        assert "toLower" in query

    def test_search_nodes_more_results_flag(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that moreResults flag is set correctly when results equal size.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        # Create exactly 'size' number of results to indicate more might exist
        mock_nodes = []
        for i in range(5):
            mock_node = create_autospec(Neo4jNode, instance=True)
            mock_node.element_id = f"4:abc:{i}"
            mock_node.labels = frozenset(["Person"])
            mock_node.items.return_value = [("name", f"Person{i}")]
            mock_nodes.append({"n": mock_node})

        mock_client = MagicMock()
        mock_client.execute_query.return_value = mock_nodes
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act - request with size=5
        response = client.get(
            "/api/neo4j/search/node/full?q=Person&size=5",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["moreResults"] is True


class TestNodeSearchErrors:
    """Test node search error scenarios."""

    def test_search_nodes_missing_query_returns_422(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that missing 'q' parameter returns 422.

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

        # Act - missing 'q' parameter
        response = client.get(
            "/api/neo4j/search/node/full",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422

    def test_search_nodes_missing_api_key_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that missing API key returns 403.

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

        # Act - no API key header
        response = client.get(
            "/api/neo4j/search/node/full?q=Alice",
        )

        # Assert
        assert response.status_code == 403

    def test_search_nodes_invalid_api_key_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that invalid API key returns 403.

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

        # Act - wrong API key
        response = client.get(
            "/api/neo4j/search/node/full?q=Alice",
            headers={"X-API-Key": "wrong-api-key"},
        )

        # Assert
        assert response.status_code == 403

    def test_search_nodes_invalid_database_returns_404(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that nonexistent database returns 404.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        # Simulate database not found error from Neo4j with proper error code
        db_not_found_error = ClientError("Database 'nonexistent' does not exist")
        db_not_found_error.code = "Neo.ClientError.Database.DatabaseNotFound"
        mock_client.execute_query.side_effect = db_not_found_error
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/nonexistent/search/node/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "DATABASE_NOT_FOUND"

    def test_search_nodes_neo4j_unavailable_returns_503(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that Neo4j unavailable returns 503.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        # No neo4j_client set on app.state
        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/neo4j/search/node/full?q=Alice",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "NEO4J_UNAVAILABLE"

    def test_search_nodes_unexpected_neo4j_error_raises(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that unexpected Neo4j errors are re-raised.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        # Simulate an unexpected ClientError (not database not found)
        mock_client.execute_query.side_effect = ClientError("Unexpected internal error")
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app, raise_server_exceptions=False)

        # Act
        response = client.get(
            "/api/neo4j/search/node/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert - unexpected errors result in 500 Internal Server Error
        assert response.status_code == 500


class TestNodeSearchParameters:
    """Test node search parameter validation."""

    def test_search_nodes_default_size_is_20(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that default size is 20.

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

        # Act - no size parameter
        response = client.get(
            "/api/neo4j/search/node/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        params = call_args.kwargs.get("parameters", {})
        assert params.get("size") == 20

    def test_search_nodes_default_from_is_0(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that default from is 0.

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

        # Act - no from parameter
        response = client.get(
            "/api/neo4j/search/node/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        params = call_args.kwargs.get("parameters", {})
        assert params.get("from_param") == 0

    def test_search_nodes_fuzziness_accepted(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that fuzziness parameter is accepted (but not used in v1.0).

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

        # Act - with fuzziness parameter
        response = client.get(
            "/api/neo4j/search/node/full?q=test&fuzziness=0.8",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200

    def test_search_nodes_size_validation_max_1000(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that size > 1000 returns validation error.

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

        # Act - size exceeds max
        response = client.get(
            "/api/neo4j/search/node/full?q=test&size=1001",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422

    def test_search_nodes_size_validation_min_1(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that size < 1 returns validation error.

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

        # Act - size below min
        response = client.get(
            "/api/neo4j/search/node/full?q=test&size=0",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422

    def test_search_nodes_from_validation_min_0(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that from < 0 returns validation error.

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

        # Act - from below min
        response = client.get(
            "/api/neo4j/search/node/full?q=test&from=-1",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422

    def test_search_nodes_fuzziness_validation_max_1(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that fuzziness > 1.0 returns validation error.

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

        # Act - fuzziness exceeds max
        response = client.get(
            "/api/neo4j/search/node/full?q=test&fuzziness=1.5",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422

    def test_search_nodes_fuzziness_validation_min_0(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that fuzziness < 0.0 returns validation error.

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

        # Act - fuzziness below min
        response = client.get(
            "/api/neo4j/search/node/full?q=test&fuzziness=-0.1",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422


class TestEdgeSearchSuccess:
    """Test successful edge search scenarios."""

    def test_search_edges_returns_200_with_results(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that valid edge search returns 200 with results.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        # Create mock source and target nodes
        mock_source = create_autospec(Neo4jNode, instance=True)
        mock_source.element_id = "4:abc:1"

        mock_target = create_autospec(Neo4jNode, instance=True)
        mock_target.element_id = "4:abc:2"

        # Create mock relationship
        mock_rel = create_autospec(Neo4jRelationship, instance=True)
        mock_rel.element_id = "5:abc:100"
        mock_rel.type = "WORKS_FOR"
        mock_rel.items.return_value = [("since", "2020-01-15"), ("role", "Engineer")]

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"r": mock_rel, "source": mock_source, "target": mock_target}
        ]
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/neo4j/search/edge/full?q=Engineer",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "edge"
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == "5:abc:100"
        assert data["results"][0]["type"] == "WORKS_FOR"
        assert data["results"][0]["source"] == "4:abc:1"
        assert data["results"][0]["target"] == "4:abc:2"
        assert data["results"][0]["properties"]["role"] == "Engineer"

    def test_search_edges_returns_empty_results(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that edge search with no matches returns empty results.

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
        response = client.get(
            "/api/neo4j/search/edge/full?q=NonexistentRelationship",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "edge"
        assert data["totalHits"] == 0
        assert data["results"] == []

    def test_search_edges_pagination_with_size_and_from(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that pagination parameters are passed correctly for edges.

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
        response = client.get(
            "/api/neo4j/search/edge/full?q=test&size=50&from=100",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        params = call_args.kwargs.get("parameters", {})
        assert params.get("size") == 50
        assert params.get("from_param") == 100

    def test_search_edges_response_format_matches_spec(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that edge response format matches Linkurious spec.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_source = create_autospec(Neo4jNode, instance=True)
        mock_source.element_id = "4:abc:10"

        mock_target = create_autospec(Neo4jNode, instance=True)
        mock_target.element_id = "4:abc:20"

        mock_rel = create_autospec(Neo4jRelationship, instance=True)
        mock_rel.element_id = "5:abc:200"
        mock_rel.type = "KNOWS"
        mock_rel.items.return_value = [("since", 2020)]

        mock_client = MagicMock()
        mock_client.execute_query.return_value = [
            {"r": mock_rel, "source": mock_source, "target": mock_target}
        ]
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/neo4j/search/edge/full?q=2020",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Check response structure
        assert "type" in data
        assert "totalHits" in data
        assert "moreResults" in data
        assert "results" in data
        # Check result structure for edge
        result = data["results"][0]
        assert "id" in result
        assert "type" in result
        assert "source" in result
        assert "target" in result
        assert "properties" in result
        # Verify labels is None for edge results (unified model includes all fields)
        assert result.get("labels") is None

    def test_search_edges_more_results_flag(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that moreResults flag is set correctly when results equal size.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        # Create exactly 'size' number of results
        mock_results = []
        for i in range(5):
            mock_source = create_autospec(Neo4jNode, instance=True)
            mock_source.element_id = f"4:abc:{i*2}"

            mock_target = create_autospec(Neo4jNode, instance=True)
            mock_target.element_id = f"4:abc:{i*2+1}"

            mock_rel = create_autospec(Neo4jRelationship, instance=True)
            mock_rel.element_id = f"5:abc:{i}"
            mock_rel.type = "REL"
            mock_rel.items.return_value = [("prop", f"value{i}")]

            mock_results.append(
                {"r": mock_rel, "source": mock_source, "target": mock_target}
            )

        mock_client = MagicMock()
        mock_client.execute_query.return_value = mock_results
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act - request with size=5
        response = client.get(
            "/api/neo4j/search/edge/full?q=value&size=5",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["moreResults"] is True


class TestEdgeSearchErrors:
    """Test edge search error scenarios."""

    def test_search_edges_missing_query_returns_422(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that missing 'q' parameter returns 422.

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

        # Act - missing 'q' parameter
        response = client.get(
            "/api/neo4j/search/edge/full",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422

    def test_search_edges_missing_api_key_returns_403(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that missing API key returns 403 for edge search.

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

        # Act - no API key header
        response = client.get(
            "/api/neo4j/search/edge/full?q=test",
        )

        # Assert
        assert response.status_code == 403

    def test_search_edges_invalid_database_returns_404(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that nonexistent database returns 404 for edge search.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        db_not_found_error = ClientError("Database 'nonexistent' does not exist")
        db_not_found_error.code = "Neo.ClientError.Database.DatabaseNotFound"
        mock_client.execute_query.side_effect = db_not_found_error
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/nonexistent/search/edge/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "DATABASE_NOT_FOUND"

    def test_search_edges_neo4j_unavailable_returns_503(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that Neo4j unavailable returns 503 for edge search.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        # No neo4j_client set on app.state
        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app)

        # Act
        response = client.get(
            "/api/neo4j/search/edge/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "NEO4J_UNAVAILABLE"

    def test_search_edges_unexpected_neo4j_error_raises(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that unexpected Neo4j errors are re-raised for edge search.

        Args:
            settings_fixture: Test settings with configured values.
        """
        # Arrange
        app = FastAPI()
        app.include_router(router)

        mock_client = MagicMock()
        # Simulate an unexpected ClientError (not database not found)
        mock_client.execute_query.side_effect = ClientError("Unexpected internal error")
        app.state.neo4j_client = mock_client

        app.dependency_overrides[get_settings] = lambda: settings_fixture

        client = TestClient(app, raise_server_exceptions=False)

        # Act
        response = client.get(
            "/api/neo4j/search/edge/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert - unexpected errors result in 500 Internal Server Error
        assert response.status_code == 500


class TestEdgeSearchParameters:
    """Test edge search parameter validation."""

    def test_search_edges_default_size_is_20(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that default size is 20 for edge search.

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

        # Act - no size parameter
        response = client.get(
            "/api/neo4j/search/edge/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        params = call_args.kwargs.get("parameters", {})
        assert params.get("size") == 20

    def test_search_edges_default_from_is_0(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that default from is 0 for edge search.

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

        # Act - no from parameter
        response = client.get(
            "/api/neo4j/search/edge/full?q=test",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 200
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        params = call_args.kwargs.get("parameters", {})
        assert params.get("from_param") == 0

    def test_search_edges_size_validation_max_1000(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that size > 1000 returns validation error for edge search.

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

        # Act - size exceeds max
        response = client.get(
            "/api/neo4j/search/edge/full?q=test&size=1001",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422

    def test_search_edges_from_validation_min_0(
        self,
        settings_fixture: Settings,
    ) -> None:
        """Test that from < 0 returns validation error for edge search.

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

        # Act - from below min
        response = client.get(
            "/api/neo4j/search/edge/full?q=test&from=-1",
            headers={"X-API-Key": "test-api-key-12345"},
        )

        # Assert
        assert response.status_code == 422
