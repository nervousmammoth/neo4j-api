"""Unit tests for Pydantic models.

Tests follow TDD principles and ensure 100% coverage for app.models.
"""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from app.models import (
    Edge,
    EdgeData,
    Error,
    ErrorResponse,
    Node,
    NodeData,
    QueryMeta,
    QueryRequest,
    QueryResponse,
    SearchResponse,
    SearchResult,
    SuccessResponse,
)


class TestErrorModel:
    """Test cases for the Error model."""

    def test_error_creation_with_required_fields(self) -> None:
        """Test creating Error with only required fields (code and message)."""
        error = Error(code="NODE_NOT_FOUND", message="Node with ID '12345' not found")

        assert error.code == "NODE_NOT_FOUND"
        assert error.message == "Node with ID '12345' not found"
        assert error.details == {}

    def test_error_creation_with_details(self) -> None:
        """Test creating Error with optional details field."""
        error = Error(
            code="VALIDATION_ERROR",
            message="Query validation failed",
            details={"forbidden_keyword": "CREATE", "line": 1},
        )

        assert error.code == "VALIDATION_ERROR"
        assert error.message == "Query validation failed"
        assert error.details == {"forbidden_keyword": "CREATE", "line": 1}

    def test_error_serialization_without_details(self) -> None:
        """Test Error serialization to dict without details defaults to empty dict."""
        error = Error(code="AUTH_FAILED", message="Invalid API key")

        result = error.model_dump()

        assert result == {
            "code": "AUTH_FAILED",
            "message": "Invalid API key",
            "details": {},
        }

    def test_error_serialization_with_details(self) -> None:
        """Test Error serialization to dict with details."""
        error = Error(
            code="DATABASE_ERROR",
            message="Connection failed",
            details={"database": "neo4j", "timeout": 5000},
        )

        result = error.model_dump()

        assert result == {
            "code": "DATABASE_ERROR",
            "message": "Connection failed",
            "details": {"database": "neo4j", "timeout": 5000},
        }

    def test_error_serialization_includes_empty_details(self) -> None:
        """Test Error serialization always includes details (even when empty)."""
        error = Error(code="TEST_ERROR", message="Test message")

        result = error.model_dump()

        assert result == {
            "code": "TEST_ERROR",
            "message": "Test message",
            "details": {},
        }
        assert "details" in result

    def test_error_field_validation_missing_code(self) -> None:
        """Test that Error requires code field."""
        with pytest.raises(ValidationError) as exc_info:
            Error(message="Missing code field")

        assert "code" in str(exc_info.value)

    def test_error_field_validation_missing_message(self) -> None:
        """Test that Error requires message field."""
        with pytest.raises(ValidationError) as exc_info:
            Error(code="TEST_CODE")

        assert "message" in str(exc_info.value)

    def test_error_details_accepts_any_dict(self) -> None:
        """Test that details field accepts various dict structures."""
        # Nested dict
        error1 = Error(
            code="COMPLEX_ERROR",
            message="Complex details",
            details={"nested": {"key": "value"}, "list": [1, 2, 3]},
        )
        assert error1.details["nested"]["key"] == "value"

        # Empty dict
        error2 = Error(code="EMPTY_DETAILS", message="Empty", details={})
        assert error2.details == {}


class TestErrorResponseModel:
    """Test cases for the ErrorResponse model."""

    def test_error_response_creation(self) -> None:
        """Test creating ErrorResponse with nested Error object."""
        error = Error(code="NOT_FOUND", message="Resource not found")
        response = ErrorResponse(error=error)

        assert response.error.code == "NOT_FOUND"
        assert response.error.message == "Resource not found"
        assert response.error.details == {}

    def test_error_response_creation_with_details(self) -> None:
        """Test creating ErrorResponse with Error containing details."""
        error = Error(
            code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "query", "reason": "Contains forbidden keyword"},
        )
        response = ErrorResponse(error=error)

        assert response.error.code == "VALIDATION_ERROR"
        assert response.error.details["field"] == "query"

    def test_error_response_serialization(self) -> None:
        """Test ErrorResponse serialization to nested dict structure."""
        error = Error(
            code="NODE_NOT_FOUND",
            message="Node with ID '12345' not found",
            details={"node_id": "12345", "database": "neo4j"},
        )
        response = ErrorResponse(error=error)

        result = response.model_dump()

        assert result == {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Node with ID '12345' not found",
                "details": {"node_id": "12345", "database": "neo4j"},
            }
        }

    def test_error_response_serialization_without_details(self) -> None:
        """Test ErrorResponse serialization when Error has no details defaults to empty dict."""
        error = Error(code="AUTH_REQUIRED", message="Authentication required")
        response = ErrorResponse(error=error)

        result = response.model_dump()

        assert result == {
            "error": {
                "code": "AUTH_REQUIRED",
                "message": "Authentication required",
                "details": {},
            }
        }

    def test_error_response_serialization_always_includes_details(self) -> None:
        """Test ErrorResponse serialization always includes details (empty dict when no details)."""
        error = Error(code="SIMPLE_ERROR", message="Simple error message")
        response = ErrorResponse(error=error)

        result = response.model_dump()

        assert result == {
            "error": {
                "code": "SIMPLE_ERROR",
                "message": "Simple error message",
                "details": {},
            }
        }
        assert "details" in result["error"]

    def test_error_response_json_structure_matches_spec(self) -> None:
        """Test that JSON structure matches Linkurious API specification."""
        error = Error(
            code="WRITE_OPERATION_FORBIDDEN",
            message="Write operations are not allowed",
            details={"forbidden_keyword": "CREATE", "query": "CREATE (n) RETURN n"},
        )
        response = ErrorResponse(error=error)

        json_dict = response.model_dump()

        # Verify nested structure as per spec
        assert "error" in json_dict
        assert "code" in json_dict["error"]
        assert "message" in json_dict["error"]
        assert "details" in json_dict["error"]
        assert json_dict["error"]["code"] == "WRITE_OPERATION_FORBIDDEN"

    def test_error_response_from_dict(self) -> None:
        """Test creating ErrorResponse from dictionary (deserialization)."""
        data = {
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Connection timeout",
                "details": {"timeout_ms": 5000},
            }
        }

        response = ErrorResponse(**data)

        assert response.error.code == "DATABASE_ERROR"
        assert response.error.message == "Connection timeout"
        assert response.error.details["timeout_ms"] == 5000

    def test_error_response_validation_requires_error(self) -> None:
        """Test that ErrorResponse requires error field."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(**{})  # type: ignore[arg-type]

        assert "error" in str(exc_info.value)


class TestSuccessResponseModel:
    """Test cases for the SuccessResponse model."""

    def test_success_response_with_defaults(self) -> None:
        """Test creating SuccessResponse with default values."""
        response = SuccessResponse()

        assert response.success is True
        assert response.message is None

    def test_success_response_with_message(self) -> None:
        """Test creating SuccessResponse with custom message."""
        response = SuccessResponse(message="Operation completed successfully")

        assert response.success is True
        assert response.message == "Operation completed successfully"

    def test_success_response_explicit_success_true(self) -> None:
        """Test creating SuccessResponse with explicit success=True."""
        response = SuccessResponse(success=True, message="All good")

        assert response.success is True
        assert response.message == "All good"

    def test_success_response_serialization_with_defaults(self) -> None:
        """Test SuccessResponse serialization with default values."""
        response = SuccessResponse()

        result = response.model_dump()

        assert result == {"success": True, "message": None}

    def test_success_response_serialization_with_message(self) -> None:
        """Test SuccessResponse serialization with message."""
        response = SuccessResponse(message="Query executed successfully")

        result = response.model_dump()

        assert result == {"success": True, "message": "Query executed successfully"}

    def test_success_response_serialization_exclude_none(self) -> None:
        """Test SuccessResponse serialization excluding None values."""
        response = SuccessResponse()

        result = response.model_dump(exclude_none=True)

        assert result == {"success": True}
        assert "message" not in result

    def test_success_response_from_dict(self) -> None:
        """Test creating SuccessResponse from dictionary."""
        data = {"success": True, "message": "Database updated"}

        response = SuccessResponse(**data)

        assert response.success is True
        assert response.message == "Database updated"

    def test_success_response_rejects_success_false(self) -> None:
        """Test that SuccessResponse raises a validation error for success=False."""
        with pytest.raises(ValidationError) as exc_info:
            SuccessResponse(success=False)  # type: ignore[arg-type]

        assert "success" in str(exc_info.value)


class TestQueryRequestModel:
    """Test cases for the QueryRequest model."""

    def test_query_request_with_query_only(self) -> None:
        """Test creating QueryRequest with only query field."""
        request = QueryRequest(query="MATCH (n) RETURN n LIMIT 10")

        assert request.query == "MATCH (n) RETURN n LIMIT 10"
        assert request.parameters == {}

    def test_query_request_with_parameters(self) -> None:
        """Test creating QueryRequest with query and parameters."""
        request = QueryRequest(
            query="MATCH (n:Person) WHERE n.name = $name RETURN n",
            parameters={"name": "John"},
        )

        assert request.query == "MATCH (n:Person) WHERE n.name = $name RETURN n"
        assert request.parameters == {"name": "John"}

    def test_query_request_empty_query_fails(self) -> None:
        """Test that empty query string raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query="")

        assert "query" in str(exc_info.value)

    def test_query_request_missing_query_fails(self) -> None:
        """Test that missing query field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(parameters={"key": "value"})  # type: ignore[call-arg]

        assert "query" in str(exc_info.value)

    def test_query_request_serialization(self) -> None:
        """Test QueryRequest serialization to dict."""
        request = QueryRequest(
            query="MATCH (n) RETURN n",
            parameters={"limit": 100},
        )

        result = request.model_dump()

        assert result == {
            "query": "MATCH (n) RETURN n",
            "parameters": {"limit": 100},
        }

    def test_query_request_serialization_default_parameters(self) -> None:
        """Test QueryRequest serialization with default empty parameters."""
        request = QueryRequest(query="MATCH (n) RETURN n")

        result = request.model_dump()

        assert result == {
            "query": "MATCH (n) RETURN n",
            "parameters": {},
        }

    def test_query_request_from_dict(self) -> None:
        """Test creating QueryRequest from dictionary."""
        data = {
            "query": "MATCH (n:Movie) WHERE n.year = $year RETURN n.title",
            "parameters": {"year": 2023},
        }

        request = QueryRequest(**data)

        assert request.query == "MATCH (n:Movie) WHERE n.year = $year RETURN n.title"
        assert request.parameters["year"] == 2023

    def test_query_request_complex_parameters(self) -> None:
        """Test QueryRequest with complex parameter types."""
        request = QueryRequest(
            query="MATCH (n) WHERE n.id IN $ids RETURN n",
            parameters={
                "ids": [1, 2, 3],
                "nested": {"key": "value"},
                "flag": True,
                "count": 42,
            },
        )

        assert request.parameters["ids"] == [1, 2, 3]
        assert request.parameters["nested"]["key"] == "value"
        assert request.parameters["flag"] is True
        assert request.parameters["count"] == 42


class TestNodeDataModel:
    """Test cases for the NodeData model."""

    def test_node_data_creation(self) -> None:
        """Test creating NodeData with categories and properties."""
        data = NodeData(
            categories=["Person", "Employee"],
            properties={"name": "John", "age": 30},
        )

        assert data.categories == ["Person", "Employee"]
        assert data.properties == {"name": "John", "age": 30}

    def test_node_data_empty_categories(self) -> None:
        """Test NodeData with empty categories list."""
        data = NodeData(categories=[], properties={"key": "value"})

        assert data.categories == []
        assert data.properties == {"key": "value"}

    def test_node_data_empty_properties(self) -> None:
        """Test NodeData with empty properties dict."""
        data = NodeData(categories=["Label"], properties={})

        assert data.categories == ["Label"]
        assert data.properties == {}

    def test_node_data_serialization(self) -> None:
        """Test NodeData serialization to dict."""
        data = NodeData(
            categories=["Movie"],
            properties={"title": "The Matrix", "year": 1999},
        )

        result = data.model_dump()

        assert result == {
            "categories": ["Movie"],
            "properties": {"title": "The Matrix", "year": 1999},
        }

    def test_node_data_missing_categories_fails(self) -> None:
        """Test that missing categories raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            NodeData(properties={"key": "value"})  # type: ignore[call-arg]

        assert "categories" in str(exc_info.value)

    def test_node_data_missing_properties_fails(self) -> None:
        """Test that missing properties raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            NodeData(categories=["Label"])  # type: ignore[call-arg]

        assert "properties" in str(exc_info.value)


class TestNodeModel:
    """Test cases for the Node model."""

    def test_node_creation(self) -> None:
        """Test creating Node with id and data."""
        node = Node(
            id="123",
            data=NodeData(
                categories=["Person"],
                properties={"name": "Alice"},
            ),
        )

        assert node.id == "123"
        assert node.data.categories == ["Person"]
        assert node.data.properties["name"] == "Alice"

    def test_node_serialization(self) -> None:
        """Test Node serialization to Linkurious format."""
        node = Node(
            id="456",
            data=NodeData(
                categories=["Company", "Tech"],
                properties={"name": "Acme", "employees": 100},
            ),
        )

        result = node.model_dump()

        assert result == {
            "id": "456",
            "data": {
                "categories": ["Company", "Tech"],
                "properties": {"name": "Acme", "employees": 100},
            },
        }

    def test_node_from_dict(self) -> None:
        """Test creating Node from dictionary."""
        data = {
            "id": "789",
            "data": {
                "categories": ["City"],
                "properties": {"name": "Berlin", "population": 3645000},
            },
        }

        node = Node(**data)

        assert node.id == "789"
        assert node.data.categories == ["City"]
        assert node.data.properties["population"] == 3645000

    def test_node_missing_id_fails(self) -> None:
        """Test that missing id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Node(data=NodeData(categories=["Label"], properties={}))  # type: ignore[call-arg]

        assert "id" in str(exc_info.value)

    def test_node_missing_data_fails(self) -> None:
        """Test that missing data raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Node(id="123")  # type: ignore[call-arg]

        assert "data" in str(exc_info.value)


class TestEdgeDataModel:
    """Test cases for the EdgeData model."""

    def test_edge_data_creation(self) -> None:
        """Test creating EdgeData with type and properties."""
        data = EdgeData(
            type="KNOWS",
            properties={"since": 2020, "strength": 0.9},
        )

        assert data.type == "KNOWS"
        assert data.properties == {"since": 2020, "strength": 0.9}

    def test_edge_data_empty_properties(self) -> None:
        """Test EdgeData with empty properties dict."""
        data = EdgeData(type="FOLLOWS", properties={})

        assert data.type == "FOLLOWS"
        assert data.properties == {}

    def test_edge_data_serialization(self) -> None:
        """Test EdgeData serialization to dict."""
        data = EdgeData(
            type="WORKS_AT",
            properties={"role": "Engineer", "since": 2019},
        )

        result = data.model_dump()

        assert result == {
            "type": "WORKS_AT",
            "properties": {"role": "Engineer", "since": 2019},
        }

    def test_edge_data_missing_type_fails(self) -> None:
        """Test that missing type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EdgeData(properties={})  # type: ignore[call-arg]

        assert "type" in str(exc_info.value)

    def test_edge_data_missing_properties_fails(self) -> None:
        """Test that missing properties raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EdgeData(type="KNOWS")  # type: ignore[call-arg]

        assert "properties" in str(exc_info.value)


class TestEdgeModel:
    """Test cases for the Edge model."""

    def test_edge_creation(self) -> None:
        """Test creating Edge with all required fields."""
        edge = Edge(
            id="rel_1",
            source="node_1",
            target="node_2",
            data=EdgeData(type="KNOWS", properties={"since": 2020}),
        )

        assert edge.id == "rel_1"
        assert edge.source == "node_1"
        assert edge.target == "node_2"
        assert edge.data.type == "KNOWS"
        assert edge.data.properties["since"] == 2020

    def test_edge_serialization(self) -> None:
        """Test Edge serialization to Linkurious format."""
        edge = Edge(
            id="100",
            source="1",
            target="2",
            data=EdgeData(type="ACTED_IN", properties={"role": "Neo"}),
        )

        result = edge.model_dump()

        assert result == {
            "id": "100",
            "source": "1",
            "target": "2",
            "data": {
                "type": "ACTED_IN",
                "properties": {"role": "Neo"},
            },
        }

    def test_edge_from_dict(self) -> None:
        """Test creating Edge from dictionary."""
        data = {
            "id": "200",
            "source": "10",
            "target": "20",
            "data": {
                "type": "DIRECTED",
                "properties": {"year": 1999},
            },
        }

        edge = Edge(**data)

        assert edge.id == "200"
        assert edge.source == "10"
        assert edge.target == "20"
        assert edge.data.type == "DIRECTED"

    def test_edge_missing_source_fails(self) -> None:
        """Test that missing source raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Edge(
                id="1",
                target="2",
                data=EdgeData(type="REL", properties={}),
            )  # type: ignore[call-arg]

        assert "source" in str(exc_info.value)

    def test_edge_missing_target_fails(self) -> None:
        """Test that missing target raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Edge(
                id="1",
                source="2",
                data=EdgeData(type="REL", properties={}),
            )  # type: ignore[call-arg]

        assert "target" in str(exc_info.value)


class TestQueryMetaModel:
    """Test cases for the QueryMeta model."""

    def test_query_meta_creation(self) -> None:
        """Test creating QueryMeta with all fields."""
        meta = QueryMeta(
            query_type="r",
            records_returned=42,
            execution_time_ms=15.5,
        )

        assert meta.query_type == "r"
        assert meta.records_returned == 42
        assert meta.execution_time_ms == 15.5

    def test_query_meta_read_type(self) -> None:
        """Test QueryMeta with read query type."""
        meta = QueryMeta(
            query_type="r",
            records_returned=100,
            execution_time_ms=25.0,
        )

        assert meta.query_type == "r"

    def test_query_meta_write_type(self) -> None:
        """Test QueryMeta with write query type."""
        meta = QueryMeta(
            query_type="w",
            records_returned=1,
            execution_time_ms=50.0,
        )

        assert meta.query_type == "w"

    def test_query_meta_serialization(self) -> None:
        """Test QueryMeta serialization to dict."""
        meta = QueryMeta(
            query_type="r",
            records_returned=10,
            execution_time_ms=5.25,
        )

        result = meta.model_dump()

        assert result == {
            "query_type": "r",
            "records_returned": 10,
            "execution_time_ms": 5.25,
        }

    def test_query_meta_zero_records(self) -> None:
        """Test QueryMeta with zero records returned."""
        meta = QueryMeta(
            query_type="r",
            records_returned=0,
            execution_time_ms=1.0,
        )

        assert meta.records_returned == 0

    def test_query_meta_missing_query_type_fails(self) -> None:
        """Test that missing query_type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QueryMeta(records_returned=10, execution_time_ms=5.0)  # type: ignore[call-arg]

        assert "query_type" in str(exc_info.value)

    def test_query_meta_invalid_query_type_fails(self) -> None:
        """Test that invalid query_type value raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QueryMeta(
                query_type="x",  # type: ignore[arg-type]
                records_returned=10,
                execution_time_ms=5.0,
            )

        assert "query_type" in str(exc_info.value)


class TestQueryResponseModel:
    """Test cases for the QueryResponse model."""

    def test_query_response_empty_results(self) -> None:
        """Test QueryResponse with empty nodes and edges."""
        response = QueryResponse(nodes=[], edges=[])

        assert response.nodes == []
        assert response.edges == []
        assert response.truncated_by_limit is False
        assert response.meta is None

    def test_query_response_with_nodes(self) -> None:
        """Test QueryResponse with nodes only."""
        nodes = [
            Node(
                id="1",
                data=NodeData(categories=["Person"], properties={"name": "Alice"}),
            ),
            Node(
                id="2",
                data=NodeData(categories=["Person"], properties={"name": "Bob"}),
            ),
        ]

        response = QueryResponse(nodes=nodes, edges=[])

        assert len(response.nodes) == 2
        assert response.nodes[0].data.properties["name"] == "Alice"
        assert response.nodes[1].data.properties["name"] == "Bob"

    def test_query_response_with_edges(self) -> None:
        """Test QueryResponse with nodes and edges."""
        nodes = [
            Node(id="1", data=NodeData(categories=["Person"], properties={})),
            Node(id="2", data=NodeData(categories=["Person"], properties={})),
        ]
        edges = [
            Edge(
                id="100",
                source="1",
                target="2",
                data=EdgeData(type="KNOWS", properties={}),
            ),
        ]

        response = QueryResponse(nodes=nodes, edges=edges)

        assert len(response.nodes) == 2
        assert len(response.edges) == 1
        assert response.edges[0].data.type == "KNOWS"

    def test_query_response_truncated(self) -> None:
        """Test QueryResponse with truncated_by_limit=True."""
        response = QueryResponse(nodes=[], edges=[], truncated_by_limit=True)

        assert response.truncated_by_limit is True

    def test_query_response_with_meta(self) -> None:
        """Test QueryResponse with metadata."""
        meta = QueryMeta(
            query_type="r",
            records_returned=5,
            execution_time_ms=12.3,
        )

        response = QueryResponse(nodes=[], edges=[], meta=meta)

        assert response.meta is not None
        assert response.meta.query_type == "r"
        assert response.meta.records_returned == 5
        assert response.meta.execution_time_ms == 12.3

    def test_query_response_full_serialization(self) -> None:
        """Test QueryResponse full serialization to Linkurious format."""
        nodes = [
            Node(
                id="1",
                data=NodeData(
                    categories=["Movie"],
                    properties={"title": "The Matrix"},
                ),
            ),
        ]
        edges = [
            Edge(
                id="10",
                source="1",
                target="2",
                data=EdgeData(type="SEQUEL", properties={}),
            ),
        ]
        meta = QueryMeta(
            query_type="r",
            records_returned=1,
            execution_time_ms=8.5,
        )

        response = QueryResponse(
            nodes=nodes,
            edges=edges,
            truncated_by_limit=False,
            meta=meta,
        )

        result = response.model_dump(by_alias=True)

        assert result == {
            "nodes": [
                {
                    "id": "1",
                    "data": {
                        "categories": ["Movie"],
                        "properties": {"title": "The Matrix"},
                    },
                }
            ],
            "edges": [
                {
                    "id": "10",
                    "source": "1",
                    "target": "2",
                    "data": {
                        "type": "SEQUEL",
                        "properties": {},
                    },
                }
            ],
            "truncatedByLimit": False,
            "meta": {
                "query_type": "r",
                "records_returned": 1,
                "execution_time_ms": 8.5,
            },
        }

    def test_query_response_serialization_exclude_none(self) -> None:
        """Test QueryResponse serialization excluding None meta."""
        response = QueryResponse(nodes=[], edges=[])

        result = response.model_dump(exclude_none=True, by_alias=True)

        assert result == {
            "nodes": [],
            "edges": [],
            "truncatedByLimit": False,
        }
        assert "meta" not in result

    def test_query_response_from_dict(self) -> None:
        """Test creating QueryResponse from dictionary."""
        data = {
            "nodes": [
                {
                    "id": "99",
                    "data": {
                        "categories": ["City"],
                        "properties": {"name": "Paris"},
                    },
                }
            ],
            "edges": [],
            "truncatedByLimit": True,
            "meta": {
                "query_type": "r",
                "records_returned": 1,
                "execution_time_ms": 3.0,
            },
        }

        response = QueryResponse(**data)

        assert len(response.nodes) == 1
        assert response.nodes[0].id == "99"
        assert response.truncated_by_limit is True  # Alias maps to internal name
        assert response.meta is not None
        assert response.meta.query_type == "r"

    def test_query_response_missing_nodes_fails(self) -> None:
        """Test that missing nodes raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResponse(edges=[])  # type: ignore[call-arg]

        assert "nodes" in str(exc_info.value)

    def test_query_response_missing_edges_fails(self) -> None:
        """Test that missing edges raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResponse(nodes=[])  # type: ignore[call-arg]

        assert "edges" in str(exc_info.value)


class TestSearchResultModel:
    """Test cases for the SearchResult model."""

    def test_search_result_creation_for_node(self) -> None:
        """Test creating SearchResult for a node search result."""
        result = SearchResult(
            id="123",
            labels=["Person", "Employee"],
            properties={"name": "Alice", "age": 30},
        )

        assert result.id == "123"
        assert result.labels == ["Person", "Employee"]
        assert result.properties == {"name": "Alice", "age": 30}
        assert result.type is None
        assert result.source is None
        assert result.target is None

    def test_search_result_creation_for_edge(self) -> None:
        """Test creating SearchResult for an edge search result."""
        result = SearchResult(
            id="789",
            type="WORKS_FOR",
            source="123",
            target="456",
            properties={"since": "2020-01-15", "role": "Engineer"},
        )

        assert result.id == "789"
        assert result.type == "WORKS_FOR"
        assert result.source == "123"
        assert result.target == "456"
        assert result.properties == {"since": "2020-01-15", "role": "Engineer"}
        assert result.labels is None

    def test_search_result_serialization_node(self) -> None:
        """Test SearchResult serialization for node."""
        result = SearchResult(
            id="100",
            labels=["Movie"],
            properties={"title": "The Matrix", "year": 1999},
        )

        data = result.model_dump()

        assert data == {
            "id": "100",
            "labels": ["Movie"],
            "type": None,
            "properties": {"title": "The Matrix", "year": 1999},
            "source": None,
            "target": None,
        }

    def test_search_result_serialization_edge(self) -> None:
        """Test SearchResult serialization for edge."""
        result = SearchResult(
            id="200",
            type="DIRECTED",
            source="10",
            target="20",
            properties={"year": 1999},
        )

        data = result.model_dump()

        assert data == {
            "id": "200",
            "labels": None,
            "type": "DIRECTED",
            "properties": {"year": 1999},
            "source": "10",
            "target": "20",
        }

    def test_search_result_serialization_exclude_none(self) -> None:
        """Test SearchResult serialization excluding None values."""
        result = SearchResult(
            id="100",
            labels=["Person"],
            properties={"name": "Alice"},
        )

        data = result.model_dump(exclude_none=True)

        assert data == {
            "id": "100",
            "labels": ["Person"],
            "properties": {"name": "Alice"},
        }
        assert "type" not in data
        assert "source" not in data
        assert "target" not in data

    def test_search_result_empty_properties(self) -> None:
        """Test SearchResult with empty properties dict."""
        result = SearchResult(id="999", labels=["Label"], properties={})

        assert result.id == "999"
        assert result.properties == {}

    def test_search_result_missing_id_fails(self) -> None:
        """Test that missing id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(labels=["Person"], properties={})  # type: ignore[call-arg]

        assert "id" in str(exc_info.value)

    def test_search_result_missing_properties_fails(self) -> None:
        """Test that missing properties raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(id="123", labels=["Person"])  # type: ignore[call-arg]

        assert "properties" in str(exc_info.value)

    def test_search_result_from_dict_node(self) -> None:
        """Test creating SearchResult from dictionary (node)."""
        data = {
            "id": "50",
            "labels": ["City"],
            "properties": {"name": "Berlin", "population": 3645000},
        }

        result = SearchResult(**data)

        assert result.id == "50"
        assert result.labels == ["City"]
        assert result.properties["population"] == 3645000

    def test_search_result_from_dict_edge(self) -> None:
        """Test creating SearchResult from dictionary (edge)."""
        data = {
            "id": "60",
            "type": "LOCATED_IN",
            "source": "1",
            "target": "2",
            "properties": {"since": 2010},
        }

        result = SearchResult(**data)

        assert result.id == "60"
        assert result.type == "LOCATED_IN"
        assert result.source == "1"
        assert result.target == "2"

    def test_search_result_mixed_fields_fails(self) -> None:
        """Test that SearchResult with both node and edge fields fails."""
        with pytest.raises(ValidationError, match="cannot have both node-specific"):
            SearchResult(
                id="1",
                labels=["Person"],
                type="KNOWS",
                source="2",
                target="3",
                properties={},
            )

    def test_search_result_incomplete_edge_fails(self) -> None:
        """Test that SearchResult with incomplete edge fields fails."""
        with pytest.raises(ValidationError, match="all required"):
            SearchResult(
                id="1",
                type="KNOWS",
                source="2",
                properties={},
            )


class TestSearchResponseModel:
    """Test cases for the SearchResponse model."""

    def test_search_response_node_type(self) -> None:
        """Test creating SearchResponse with type='node'."""
        results = [
            SearchResult(id="1", labels=["Person"], properties={"name": "Alice"}),
            SearchResult(id="2", labels=["Person"], properties={"name": "Bob"}),
        ]

        response = SearchResponse(type="node", results=results)

        assert response.type == "node"
        assert len(response.results) == 2
        assert response.total_hits is None
        assert response.more_results is None

    def test_search_response_edge_type(self) -> None:
        """Test creating SearchResponse with type='edge'."""
        results = [
            SearchResult(
                id="100",
                type="KNOWS",
                source="1",
                target="2",
                properties={"since": 2020},
            )
        ]

        response = SearchResponse(type="edge", results=results)

        assert response.type == "edge"
        assert len(response.results) == 1

    def test_search_response_with_pagination_fields(self) -> None:
        """Test SearchResponse with totalHits and moreResults."""
        results = [SearchResult(id="1", labels=["Test"], properties={})]

        response = SearchResponse(
            type="node",
            total_hits=100,
            more_results=True,
            results=results,
        )

        assert response.total_hits == 100
        assert response.more_results is True

    def test_search_response_empty_results_node(self) -> None:
        """Test SearchResponse with empty results list for node type."""
        response = SearchResponse(
            type="node",
            total_hits=0,
            more_results=False,
            results=[],
        )

        assert response.type == "node"
        assert response.results == []
        assert response.total_hits == 0
        assert response.more_results is False

    def test_search_response_empty_results_edge(self) -> None:
        """Test SearchResponse with empty results list for edge type."""
        response = SearchResponse(
            type="edge",
            total_hits=0,
            more_results=False,
            results=[],
        )

        assert response.type == "edge"
        assert response.results == []
        assert response.total_hits == 0
        assert response.more_results is False

    def test_search_response_serialization_with_aliases(self) -> None:
        """Test SearchResponse serialization uses camelCase aliases."""
        results = [SearchResult(id="1", labels=["Person"], properties={"name": "Test"})]

        response = SearchResponse(
            type="node",
            total_hits=15,
            more_results=False,
            results=results,
        )

        data = response.model_dump(by_alias=True, exclude_none=True)

        assert data == {
            "type": "node",
            "totalHits": 15,
            "moreResults": False,
            "results": [
                {
                    "id": "1",
                    "labels": ["Person"],
                    "properties": {"name": "Test"},
                }
            ],
        }

    def test_search_response_serialization_exclude_none(self) -> None:
        """Test SearchResponse serialization excluding None values."""
        response = SearchResponse(type="node", results=[])

        data = response.model_dump(by_alias=True, exclude_none=True)

        assert data == {"type": "node", "results": []}
        assert "totalHits" not in data
        assert "moreResults" not in data

    def test_search_response_invalid_type_fails(self) -> None:
        """Test that invalid type value raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResponse(
                type="invalid",  # type: ignore[arg-type]
                results=[],
            )

        assert "type" in str(exc_info.value)

    def test_search_response_missing_type_fails(self) -> None:
        """Test that missing type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResponse(results=[])  # type: ignore[call-arg]

        assert "type" in str(exc_info.value)

    def test_search_response_missing_results_fails(self) -> None:
        """Test that missing results raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResponse(type="node")  # type: ignore[call-arg]

        assert "results" in str(exc_info.value)

    def test_search_response_from_dict(self) -> None:
        """Test creating SearchResponse from dictionary with aliases."""
        data = {
            "type": "edge",
            "totalHits": 5,
            "moreResults": True,
            "results": [
                {
                    "id": "789",
                    "type": "WORKS_FOR",
                    "source": "123",
                    "target": "456",
                    "properties": {"since": "2020-01-15"},
                }
            ],
        }

        response = SearchResponse(**data)

        assert response.type == "edge"
        assert response.total_hits == 5
        assert response.more_results is True
        assert len(response.results) == 1
        assert response.results[0].type == "WORKS_FOR"

    def test_search_response_json_structure_matches_spec(self) -> None:
        """Test that JSON structure matches Linkurious API specification."""
        results = [
            SearchResult(
                id="123",
                labels=["Person"],
                properties={"name": "Alice Smith", "age": 30},
            )
        ]

        response = SearchResponse(
            type="node",
            total_hits=15,
            more_results=False,
            results=results,
        )

        json_dict = response.model_dump(by_alias=True, exclude_none=True)

        # Verify structure as per spec
        assert "type" in json_dict
        assert "totalHits" in json_dict
        assert "moreResults" in json_dict
        assert "results" in json_dict
        assert json_dict["type"] == "node"
        assert json_dict["totalHits"] == 15
        assert json_dict["moreResults"] is False
        assert len(json_dict["results"]) == 1
        assert json_dict["results"][0]["id"] == "123"
        assert json_dict["results"][0]["labels"] == ["Person"]

    def test_search_response_edge_in_node_response_fails(self) -> None:
        """Test that edge result in node response fails validation."""
        edge_result = SearchResult(
            id="1",
            type="KNOWS",
            source="2",
            target="3",
            properties={},
        )

        with pytest.raises(
            ValidationError, match="is an edge, but response type is 'node'"
        ):
            SearchResponse(type="node", results=[edge_result])

    def test_search_response_node_in_edge_response_fails(self) -> None:
        """Test that node result in edge response fails validation."""
        node_result = SearchResult(
            id="1",
            labels=["Person"],
            properties={},
        )

        with pytest.raises(
            ValidationError, match="is a node, but response type is 'edge'"
        ):
            SearchResponse(type="edge", results=[node_result])
