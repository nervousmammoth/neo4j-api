"""Pydantic models for request and response data.

This module contains all data models following Linkurious API format.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Error(BaseModel):
    """Error details structure.

    Used within ErrorResponse to provide detailed error information.

    Attributes:
        code: Machine-readable error code (e.g., "NODE_NOT_FOUND", "VALIDATION_ERROR").
        message: Human-readable error message describing what went wrong.
        details: Optional additional context or metadata about the error.

    Examples:
        >>> error = Error(
        ...     code="NODE_NOT_FOUND",
        ...     message="Node with ID '12345' not found",
        ...     details={"node_id": "12345", "database": "neo4j"}
        ... )
        >>> error.code
        'NODE_NOT_FOUND'
        >>> error.model_dump()
        {'code': 'NODE_NOT_FOUND', 'message': "Node with ID '12345' not found", 'details': {'node_id': '12345', 'database': 'neo4j'}}
    """

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        default=None, description="Optional additional error details"
    )


class ErrorResponse(BaseModel):
    """Standard error response wrapper.

    Used for all error responses across the API following Linkurious API format.
    The error field contains a nested Error object with code, message, and optional details.

    Attributes:
        error: Nested Error object containing error details.

    Examples:
        >>> error_obj = Error(
        ...     code="WRITE_OPERATION_FORBIDDEN",
        ...     message="Write operations are not allowed",
        ...     details={"forbidden_keyword": "CREATE"}
        ... )
        >>> response = ErrorResponse(error=error_obj)
        >>> response.model_dump()
        {'error': {'code': 'WRITE_OPERATION_FORBIDDEN', 'message': 'Write operations are not allowed', 'details': {'forbidden_keyword': 'CREATE'}}}
    """

    error: Error = Field(..., description="Error details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": {
                    "code": "NODE_NOT_FOUND",
                    "message": "Node with ID '12345' not found",
                    "details": {"node_id": "12345", "database": "neo4j"},
                }
            }
        }
    }


class SuccessResponse(BaseModel):
    """Generic success response for simple operations.

    Used for simple success responses without data payload.
    For operations that return data, use domain-specific response models instead.

    Attributes:
        success: Success indicator (typically True for success responses).
        message: Optional success message providing additional context.

    Examples:
        >>> response = SuccessResponse()
        >>> response.success
        True
        >>> response = SuccessResponse(message="Operation completed successfully")
        >>> response.model_dump()
        {'success': True, 'message': 'Operation completed successfully'}
    """

    success: Literal[True] = Field(default=True, description="Success indicator")
    message: str | None = Field(default=None, description="Optional success message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response.

    Response model for the GET /api/health endpoint.
    Returns API health status and Neo4j connectivity information.

    Attributes:
        status: Overall health status ("healthy" or "unhealthy").
        neo4j: Neo4j connection status ("connected" or "disconnected").
        version: API version string.
        error: Optional error message when unhealthy.

    Examples:
        >>> # Healthy response
        >>> response = HealthResponse(
        ...     status="healthy",
        ...     neo4j="connected",
        ...     version="1.0.0"
        ... )
        >>> response.model_dump()
        {'status': 'healthy', 'neo4j': 'connected', 'version': '1.0.0', 'error': None}

        >>> # Unhealthy response
        >>> response = HealthResponse(
        ...     status="unhealthy",
        ...     neo4j="disconnected",
        ...     version="1.0.0",
        ...     error="Connection refused"
        ... )
    """

    status: Literal["healthy", "unhealthy"] = Field(
        ..., description="Overall health status"
    )
    neo4j: Literal["connected", "disconnected"] = Field(
        ..., description="Neo4j connection status"
    )
    version: str | None = Field(default=None, description="API version")
    error: str | None = Field(default=None, description="Error message when unhealthy")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "neo4j": "connected",
                    "version": "1.0.0",
                },
                {
                    "status": "unhealthy",
                    "neo4j": "disconnected",
                    "version": "1.0.0",
                    "error": "Connection refused to bolt://localhost:7687",
                },
            ]
        }
    }


class Database(BaseModel):
    """Individual database information.

    Represents a single Neo4j database returned by SHOW DATABASES.

    Attributes:
        name: Database name (e.g., "neo4j", "system").
        default: Whether this is the default database.
        status: Database status (e.g., "online", "offline"). Optional.

    Examples:
        >>> db = Database(name="neo4j", default=True, status="online")
        >>> db.model_dump()
        {'name': 'neo4j', 'default': True, 'status': 'online'}
    """

    name: str = Field(..., description="Database name")
    default: bool = Field(..., description="Whether this is the default database")
    status: str | None = Field(default=None, description="Database status")


class DatabaseListResponse(BaseModel):
    """Database list response.

    Response model for the GET /api/databases endpoint.
    Returns a list of all available Neo4j databases.

    Attributes:
        databases: List of Database objects.

    Examples:
        >>> response = DatabaseListResponse(databases=[
        ...     Database(name="neo4j", default=True, status="online"),
        ...     Database(name="system", default=False, status="online"),
        ... ])
        >>> len(response.databases)
        2
    """

    databases: list[Database] = Field(..., description="List of databases")

    model_config = {
        "json_schema_extra": {
            "example": {
                "databases": [
                    {"name": "neo4j", "default": True, "status": "online"},
                    {
                        "name": "investigation_001",
                        "default": False,
                        "status": "online",
                    },
                ]
            }
        }
    }


# Query Models (Linkurious format)


class QueryRequest(BaseModel):
    """Cypher query execution request.

    Request body for POST /api/{database}/graph/query endpoint.

    Attributes:
        query: Cypher query string to execute.
        parameters: Optional query parameters for parameterized queries.

    Examples:
        >>> request = QueryRequest(
        ...     query="MATCH (n:Person) WHERE n.name = $name RETURN n",
        ...     parameters={"name": "Alice"}
        ... )
        >>> request.query
        'MATCH (n:Person) WHERE n.name = $name RETURN n'
    """

    query: str = Field(..., min_length=1, description="Cypher query string to execute")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Query parameters"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "MATCH (n:Person) WHERE n.name = $name RETURN n LIMIT 10",
                "parameters": {"name": "John"},
            }
        }
    }


class NodeData(BaseModel):
    """Node data structure for Linkurious format.

    Contains the node's labels (categories) and properties.

    Attributes:
        categories: List of node labels.
        properties: Dictionary of node properties.

    Examples:
        >>> data = NodeData(
        ...     categories=["Person", "Employee"],
        ...     properties={"name": "Alice", "age": 30}
        ... )
    """

    categories: list[str] = Field(..., description="Node labels")
    properties: dict[str, Any] = Field(..., description="Node properties")


class Node(BaseModel):
    """Node representation in Linkurious format.

    Attributes:
        id: Node ID as string.
        data: Node data containing categories and properties.

    Examples:
        >>> node = Node(
        ...     id="123",
        ...     data=NodeData(categories=["Person"], properties={"name": "Alice"})
        ... )
    """

    id: str = Field(..., description="Node ID")
    data: NodeData = Field(..., description="Node data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123",
                "data": {
                    "categories": ["Person"],
                    "properties": {"name": "Alice", "age": 30},
                },
            }
        }
    }


class EdgeData(BaseModel):
    """Edge data structure for Linkurious format.

    Contains the relationship type and properties.

    Attributes:
        type: Relationship type.
        properties: Dictionary of relationship properties.

    Examples:
        >>> data = EdgeData(type="KNOWS", properties={"since": 2020})
    """

    type: str = Field(..., description="Relationship type")
    properties: dict[str, Any] = Field(..., description="Relationship properties")


class Edge(BaseModel):
    """Edge (relationship) representation in Linkurious format.

    Attributes:
        id: Relationship ID as string.
        source: Source node ID.
        target: Target node ID.
        data: Edge data containing type and properties.

    Examples:
        >>> edge = Edge(
        ...     id="456",
        ...     source="1",
        ...     target="2",
        ...     data=EdgeData(type="KNOWS", properties={"since": 2020})
        ... )
    """

    id: str = Field(..., description="Relationship ID")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    data: EdgeData = Field(..., description="Edge data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "456",
                "source": "1",
                "target": "2",
                "data": {
                    "type": "KNOWS",
                    "properties": {"since": 2020},
                },
            }
        }
    }


class QueryMeta(BaseModel):
    """Query execution metadata.

    Attributes:
        query_type: Query type indicator ("r" for read, "w" for write).
        records_returned: Number of records returned by the query.
        execution_time_ms: Query execution time in milliseconds.

    Examples:
        >>> meta = QueryMeta(
        ...     query_type="r",
        ...     records_returned=10,
        ...     execution_time_ms=15.5
        ... )
    """

    query_type: str = Field(..., description="Query type: 'r' (read) or 'w' (write)")
    records_returned: int = Field(..., ge=0, description="Number of records returned")
    execution_time_ms: float = Field(
        ..., ge=0, description="Execution time in milliseconds"
    )


class QueryResponse(BaseModel):
    """Cypher query execution response in Linkurious format.

    Response model for POST /api/{database}/graph/query endpoint.

    Attributes:
        nodes: List of nodes from query results.
        edges: List of edges (relationships) from query results.
        truncatedByLimit: Whether results were limited by LIMIT clause.
        meta: Optional query execution metadata.

    Examples:
        >>> response = QueryResponse(
        ...     nodes=[Node(id="1", data=NodeData(categories=["Person"], properties={}))],
        ...     edges=[],
        ...     truncatedByLimit=False,
        ...     meta=QueryMeta(query_type="r", records_returned=1, execution_time_ms=5.0)
        ... )
    """

    nodes: list[Node] = Field(..., description="Nodes from query results")
    edges: list[Edge] = Field(..., description="Edges from query results")
    truncatedByLimit: bool = Field(  # noqa: N815
        default=False, description="Whether results were truncated by LIMIT"
    )
    meta: QueryMeta | None = Field(default=None, description="Query execution metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nodes": [
                    {
                        "id": "1",
                        "data": {
                            "categories": ["Person"],
                            "properties": {"name": "Alice"},
                        },
                    }
                ],
                "edges": [
                    {
                        "id": "100",
                        "source": "1",
                        "target": "2",
                        "data": {"type": "KNOWS", "properties": {}},
                    }
                ],
                "truncatedByLimit": False,
                "meta": {
                    "query_type": "r",
                    "records_returned": 1,
                    "execution_time_ms": 12.5,
                },
            }
        }
    }
