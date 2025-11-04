# Data Models Specification

## Overview

Request and response data structures (schemas) used across the API.

---

## Common Data Types

### Node

Represents a Neo4j node (vertex).

**TypeScript Schema:**
```typescript
interface Node {
  id: string                    // Node ID (as string)
  data: {
    categories: string[]        // Node labels (e.g., ["Person", "Employee"])
    properties: {               // Node properties
      [key: string]: any        // Property name → value
    }
    isVirtual?: boolean         // Optional: is this a virtual node?
    statistics?: {              // Optional: neighborhood stats
      degree?: number           // Number of neighbors
      supernode?: boolean       // Is this a supernode?
      digest?: DigestItem[]     // Neighborhood summary
    }
    readAt?: number             // Optional: read timestamp (epoch ms)
  }
}
```

**JSON Example:**
```json
{
  "id": "123",
  "data": {
    "categories": ["Person"],
    "properties": {
      "name": "Alice Smith",
      "age": 30,
      "email": "alice@example.com",
      "city": "New York"
    }
  }
}
```

### Edge (Relationship)

Represents a Neo4j relationship (edge).

**TypeScript Schema:**
```typescript
interface Edge {
  id: string                    // Relationship ID (as string)
  source: string                // Source node ID
  target: string                // Target node ID
  data: {
    type: string                // Relationship type (e.g., "WORKS_FOR")
    properties: {               // Relationship properties
      [key: string]: any        // Property name → value
    }
    isVirtual?: boolean         // Optional: is this a virtual relationship?
    readAt?: number             // Optional: read timestamp (epoch ms)
  }
}
```

**JSON Example:**
```json
{
  "id": "789",
  "source": "123",
  "target": "456",
  "data": {
    "type": "WORKS_FOR",
    "properties": {
      "since": "2020-01-15",
      "role": "Engineer",
      "department": "R&D"
    }
  }
}
```

---

## Request Models

### QueryRequest

Request body for query execution endpoint.

**TypeScript Schema:**
```typescript
interface QueryRequest {
  query: string                 // Cypher query (required)
  parameters?: {                // Query parameters (optional)
    [key: string]: any          // Parameter name → value
  }
}
```

**JSON Example:**
```json
{
  "query": "MATCH (p:Person) WHERE p.age > $age RETURN p LIMIT $limit",
  "parameters": {
    "age": 25,
    "limit": 10
  }
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="Cypher query to execute", min_length=1)
    parameters: Optional[Dict[str, Any]] = Field(
        default={},
        description="Query parameters"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "MATCH (p:Person) WHERE p.age > $age RETURN p LIMIT $limit",
                "parameters": {"age": 25, "limit": 10}
            }
        }
```

### NodeExpandRequest

Request body for node expansion endpoint.

**TypeScript Schema:**
```typescript
interface NodeExpandRequest {
  ids: string[]                 // Node IDs to expand (required, min 1)
  limit?: number                // Max neighbors per node (optional, default: 50)
  direction?: "in" | "out" | "both"  // Relationship direction (optional, default: "both")
}
```

**JSON Example:**
```json
{
  "ids": ["123", "456", "789"],
  "limit": 20,
  "direction": "both"
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class NodeExpandRequest(BaseModel):
    ids: List[str] = Field(..., description="Node IDs to expand", min_length=1)
    limit: Optional[int] = Field(
        default=50,
        description="Maximum neighbors per node",
        ge=1,
        le=1000
    )
    direction: Optional[Literal["in", "out", "both"]] = Field(
        default="both",
        description="Relationship direction"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ids": ["123", "456"],
                "limit": 20
            }
        }
```

---

## Response Models

### QueryResponse

Response for query execution and node expansion.

**TypeScript Schema:**
```typescript
interface QueryResponse {
  nodes: Node[]                 // Array of nodes
  edges: Edge[]                 // Array of relationships
  truncatedByLimit: boolean     // Results limited by query LIMIT clause
  truncatedByAccess?: boolean   // Optional: filtered by access rights
  meta?: {                      // Optional: query metadata
    query_type: string          // "r" (read) or "w" (write)
    records_returned: number
    execution_time_ms: number
  }
}
```

**JSON Example:**
```json
{
  "nodes": [
    {
      "id": "123",
      "data": {
        "categories": ["Person"],
        "properties": {"name": "Alice"}
      }
    }
  ],
  "edges": [
    {
      "id": "789",
      "source": "123",
      "target": "456",
      "data": {
        "type": "KNOWS",
        "properties": {}
      }
    }
  ],
  "truncatedByLimit": false,
  "meta": {
    "query_type": "r",
    "records_returned": 2,
    "execution_time_ms": 45
  }
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class NodeData(BaseModel):
    categories: List[str]
    properties: Dict[str, Any]

class Node(BaseModel):
    id: str
    data: NodeData

class EdgeData(BaseModel):
    type: str
    properties: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str
    data: EdgeData

class QueryMeta(BaseModel):
    query_type: str
    records_returned: int
    execution_time_ms: int

class QueryResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    truncatedByLimit: bool = False
    meta: Optional[QueryMeta] = None
```

### SearchResponse

Response for search endpoints.

**TypeScript Schema:**
```typescript
interface SearchResponse {
  type: "node" | "edge"         // Type of search
  totalHits?: number            // Total matching items (if known)
  moreResults?: boolean         // True if more results available
  results: Array<{              // Search results
    id: string
    labels?: string[]           // For nodes: labels
    type?: string               // For edges: relationship type
    properties: {
      [key: string]: any
    }
    source?: string             // For edges: source node ID
    target?: string             // For edges: target node ID
  }>
}
```

**JSON Example (Node Search):**
```json
{
  "type": "node",
  "totalHits": 15,
  "moreResults": false,
  "results": [
    {
      "id": "123",
      "labels": ["Person"],
      "properties": {
        "name": "Alice Smith",
        "age": 30
      }
    }
  ]
}
```

**JSON Example (Edge Search):**
```json
{
  "type": "edge",
  "totalHits": 5,
  "moreResults": false,
  "results": [
    {
      "id": "789",
      "type": "WORKS_FOR",
      "source": "123",
      "target": "456",
      "properties": {
        "since": "2020-01-15"
      }
    }
  ]
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal

class SearchResult(BaseModel):
    id: str
    labels: Optional[List[str]] = None      # For nodes
    type: Optional[str] = None              # For edges
    properties: Dict[str, Any]
    source: Optional[str] = None            # For edges
    target: Optional[str] = None            # For edges

class SearchResponse(BaseModel):
    type: Literal["node", "edge"]
    totalHits: Optional[int] = None
    moreResults: Optional[bool] = None
    results: List[SearchResult]
```

### SchemaResponse

Response for schema endpoints.

**TypeScript Schema:**
```typescript
interface SchemaResponse {
  types: string[]               // Array of label/type names
}
```

**JSON Example:**
```json
{
  "types": ["Person", "Company", "Product"]
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel
from typing import List

class SchemaResponse(BaseModel):
    types: List[str]
```

### DatabaseListResponse

Response for list databases endpoint.

**TypeScript Schema:**
```typescript
interface DatabaseListResponse {
  databases: Array<{
    name: string                // Database name
    default: boolean            // Is this the default database?
    status?: string             // Optional: "online", "offline", etc.
    description?: string        // Optional: human-readable description
  }>
}
```

**JSON Example:**
```json
{
  "databases": [
    {
      "name": "neo4j",
      "default": true,
      "status": "online"
    },
    {
      "name": "investigation_001",
      "default": false,
      "status": "online",
      "description": "Fraud investigation case 001"
    }
  ]
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel
from typing import List, Optional

class Database(BaseModel):
    name: str
    default: bool
    status: Optional[str] = None
    description: Optional[str] = None

class DatabaseListResponse(BaseModel):
    databases: List[Database]
```

### HealthResponse

Response for health check endpoint.

**TypeScript Schema:**
```typescript
interface HealthResponse {
  status: "healthy" | "unhealthy"
  neo4j: "connected" | "disconnected"
  version?: string              // Optional: API version
  error?: string                // Optional: error message if unhealthy
}
```

**JSON Example (Healthy):**
```json
{
  "status": "healthy",
  "neo4j": "connected",
  "version": "1.0.0"
}
```

**JSON Example (Unhealthy):**
```json
{
  "status": "unhealthy",
  "neo4j": "disconnected",
  "error": "Connection refused to bolt://localhost:7687"
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel
from typing import Optional, Literal

class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    neo4j: Literal["connected", "disconnected"]
    version: Optional[str] = None
    error: Optional[str] = None
```

---

## Error Response Model

### ErrorResponse

Standard error response format (see [error-handling.md](./error-handling.md) for full spec).

**TypeScript Schema:**
```typescript
interface ErrorResponse {
  error: {
    code: string                // Machine-readable error code
    message: string             // Human-readable error message
    details?: {                 // Optional: additional context
      [key: string]: any
    }
  }
}
```

**JSON Example:**
```json
{
  "error": {
    "code": "NODE_NOT_FOUND",
    "message": "Node with ID '12345' not found",
    "details": {
      "node_id": "12345",
      "database": "neo4j"
    }
  }
}
```

**Pydantic Model (Python):**
```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ErrorDetails(BaseModel):
    pass  # Accept any fields

class Error(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: Error
```

---

## Validation Rules

### Node ID
- **Format:** String representation of integer
- **Example:** `"123"`, not `123`
- **Validation:** Must be parseable to integer

### Database Name
- **Format:** Alphanumeric with underscores
- **Pattern:** `^[a-zA-Z0-9_]+$`
- **Max Length:** 63 characters
- **Example:** `neo4j`, `investigation_001`, `fraud_2024`

### Cypher Query
- **Min Length:** 1 character
- **Max Length:** 100,000 characters (configurable)
- **Validation:** Must not contain forbidden keywords (CREATE, DELETE, etc.)

### API Key
- **Min Length:** 16 characters
- **Format:** Base64 or hex string
- **Transmitted:** Via `X-API-Key` header only

### Fuzziness
- **Type:** Float
- **Range:** 0.0 to 1.0 (inclusive)
- **Default:** 0.7

### Pagination
- **size:** Integer, 1 to 1000, default: 20
- **from:** Integer, >= 0, default: 0

---

## Type Conversions

### Neo4j → JSON

| Neo4j Type | JSON Type | Notes |
|------------|-----------|-------|
| Integer | number | |
| Float | number | |
| String | string | |
| Boolean | boolean | |
| Date | string | ISO 8601 format: "2025-11-03" |
| DateTime | string | ISO 8601 format: "2025-11-03T12:00:00Z" |
| Time | string | ISO 8601 format: "12:00:00" |
| Duration | string | ISO 8601 duration: "P1Y2M" |
| Point | object | `{x: number, y: number, srid: number}` |
| Node | object | See Node model above |
| Relationship | object | See Edge model above |
| Path | array | Array of nodes and relationships |
| List | array | |
| Map | object | |
| null | null | |

### JSON → Neo4j Parameters

When sending parameters in queries, JSON types map to Neo4j types:

```json
{
  "parameters": {
    "name": "Alice",              // String
    "age": 30,                    // Integer
    "active": true,               // Boolean
    "salary": 50000.50,           // Float
    "tags": ["tag1", "tag2"],     // List
    "metadata": {"key": "value"}  // Map
  }
}
```

---

## Future Enhancements

### 1. Pagination Model

```typescript
interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    total: number
    page: number
    size: number
    hasNext: boolean
    hasPrevious: boolean
  }
}
```

### 2. Graph Stats Model

```typescript
interface GraphStats {
  node_count: number
  edge_count: number
  labels: string[]
  relationship_types: string[]
  db_size_bytes: number
}
```

### 3. Batch Query Request

```typescript
interface BatchQueryRequest {
  queries: Array<{
    id: string
    query: string
    parameters?: object
  }>
}
```

### 4. Query Result Metadata

```typescript
interface QueryMetadata {
  plan?: object               // Query execution plan
  notifications?: string[]    // Warnings/suggestions
  profile?: object            // Performance profiling
}
```
