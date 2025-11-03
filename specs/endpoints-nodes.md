# Node Operations Endpoints Specification

## Overview

Endpoints for retrieving nodes, expanding neighborhoods, and getting node counts.

---

## GET /api/{database}/graph/nodes/{node_id}

### Purpose
Retrieve a specific node by its ID along with its adjacent edges.

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** GET

**URL Pattern:** `/api/{database}/graph/nodes/{node_id}`

**Path Parameters:**
- `database` (string, required) - Name of the Neo4j database
- `node_id` (string, required) - Node ID (Neo4j internal ID)

**Query Parameters:**
- `withDigest` (boolean, optional) - Include neighborhood statistics
  - Default: false
- `withDegree` (boolean, optional) - Include degree (neighbor count)
  - Default: false

**Headers:**
```http
X-API-Key: your-secret-api-key
```

### Response

#### Success (200 OK)

```json
{
  "nodes": [
    {
      "id": "123",
      "data": {
        "categories": ["Person"],
        "properties": {
          "name": "Alice Smith",
          "age": 30,
          "email": "alice@example.com"
        }
      }
    }
  ],
  "edges": [
    {
      "id": "789",
      "source": "123",
      "target": "456",
      "data": {
        "type": "WORKS_FOR",
        "properties": {
          "since": "2020-01-15"
        }
      }
    }
  ]
}
```

**Schema:**
```typescript
{
  nodes: Array<{
    id: string
    data: {
      categories: string[]        // Node labels
      properties: object          // Node properties
      statistics?: {              // If withDigest=true
        degree?: number           // If withDegree=true
        supernode?: boolean
      }
    }
  }>
  edges: Array<{
    id: string
    source: string
    target: string
    data: {
      type: string
      properties: object
    }
  }>
}
```

#### Node Not Found (404)

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

#### Invalid Node ID (400)

```json
{
  "error": {
    "code": "INVALID_NODE_ID",
    "message": "Node ID must be a valid integer",
    "details": {
      "node_id": "not-a-number"
    }
  }
}
```

### Behavior

1. **Parse Node ID**
   - Convert string to integer
   - Validate format

2. **Query Node**
   ```cypher
   MATCH (n)-[r]-(m)
   WHERE id(n) = $node_id
   RETURN n, r, m
   ```

3. **Return Node + Adjacent Edges**
   - Include the requested node
   - Include all edges connected to the node
   - Include endpoint nodes of those edges

### Examples

#### Example 1: Get Node

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/neo4j/graph/nodes/123
```

**Response (200):**
```json
{
  "nodes": [
    {"id": "123", "data": {"categories": ["Person"], "properties": {"name": "Alice"}}}
  ],
  "edges": []
}
```

#### Example 2: Node Not Found

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/neo4j/graph/nodes/99999
```

**Response (404):**
```json
{
  "error": {
    "code": "NODE_NOT_FOUND",
    "message": "Node with ID '99999' not found",
    "details": {"node_id": "99999", "database": "neo4j"}
  }
}
```

---

## POST /api/{database}/graph/nodes/expand

### Purpose
Expand nodes to retrieve their neighbors and connecting relationships (Linkurious-compatible).

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** POST

**URL Pattern:** `/api/{database}/graph/nodes/expand`

**Path Parameters:**
- `database` (string, required) - Name of the Neo4j database

**Headers:**
```http
X-API-Key: your-secret-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "ids": ["123", "456"]
}
```

**Schema:**
```typescript
{
  ids: string[]              // Array of node IDs to expand
  limit?: number             // Max neighbors per node (default: 50)
  direction?: "in" | "out" | "both"  // Relationship direction (default: "both")
}
```

### Response

#### Success (200 OK)

```json
{
  "nodes": [
    {
      "id": "123",
      "data": {
        "categories": ["Person"],
        "properties": {"name": "Alice"}
      }
    },
    {
      "id": "789",
      "data": {
        "categories": ["Company"],
        "properties": {"name": "Acme Corp"}
      }
    }
  ],
  "edges": [
    {
      "id": "1011",
      "source": "123",
      "target": "789",
      "data": {
        "type": "WORKS_FOR",
        "properties": {"since": "2020"}
      }
    }
  ]
}
```

**Schema:**
Same as query response - nodes and edges arrays.

#### Empty Node IDs (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "ids",
          "message": "Field required",
          "type": "missing"
        }
      ]
    }
  }
}
```

### Behavior

1. **Parse Node IDs**
   - Convert string IDs to integers
   - Validate all IDs are valid numbers

2. **Query Neighbors**
   ```cypher
   MATCH (n)-[r]-(m)
   WHERE id(n) IN $node_ids
   RETURN n, r, m
   LIMIT $limit
   ```

3. **Return Subgraph**
   - Include all source nodes
   - Include all neighbor nodes
   - Include all connecting relationships
   - Deduplicate nodes

### Use Cases

#### 1. Single Node Expansion

Explore neighborhood of one node.

**Request:**
```json
{
  "ids": ["123"]
}
```

#### 2. Multiple Node Expansion

Explore neighborhoods of multiple nodes simultaneously.

**Request:**
```json
{
  "ids": ["123", "456", "789"]
}
```

#### 3. Limited Expansion

Limit number of neighbors to prevent overwhelming results.

**Request:**
```json
{
  "ids": ["123"],
  "limit": 10
}
```

### Examples

#### Example 1: Expand Single Node

**Request:**
```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["123"]}' \
  http://localhost/api/neo4j/graph/nodes/expand
```

**Response (200):**
```json
{
  "nodes": [
    {"id": "123", "data": {"categories": ["Person"], "properties": {"name": "Alice"}}},
    {"id": "456", "data": {"categories": ["Person"], "properties": {"name": "Bob"}}}
  ],
  "edges": [
    {"id": "789", "source": "123", "target": "456", "data": {"type": "KNOWS", "properties": {}}}
  ]
}
```

#### Example 2: Empty IDs Array

**Request:**
```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"ids": []}' \
  http://localhost/api/neo4j/graph/nodes/expand
```

**Response (422):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [{"field": "ids", "message": "Array must have at least 1 item"}]
    }
  }
}
```

---

## GET /api/{database}/graph/nodes/count

### Purpose
Get the total count of nodes in the database.

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** GET

**URL Pattern:** `/api/{database}/graph/nodes/count`

**Path Parameters:**
- `database` (string, required) - Name of the Neo4j database

**Query Parameters:** None

**Headers:**
```http
X-API-Key: your-secret-api-key
```

### Response

#### Success (200 OK)

```json
42
```

**Schema:**
```typescript
number  // Total node count
```

**Alternative format (future):**
```json
{
  "count": 42,
  "by_label": {
    "Person": 25,
    "Company": 10,
    "Product": 7
  }
}
```

#### Database Error (500)

```json
{
  "error": {
    "code": "QUERY_EXECUTION_ERROR",
    "message": "Failed to count nodes",
    "details": {
      "database": "neo4j",
      "neo4j_error": "..."
    }
  }
}
```

### Behavior

**Query:**
```cypher
MATCH (n) RETURN count(n) as count
```

**Note:** This can be slow on large databases. Consider caching or using approximate counts.

### Examples

#### Example 1: Get Node Count

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/neo4j/graph/nodes/count
```

**Response (200):**
```json
15247
```

---

## GET /api/{database}/graph/edges/count

### Purpose
Get the total count of relationships in the database.

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** GET

**URL Pattern:** `/api/{database}/graph/edges/count`

**Path Parameters:**
- `database` (string, required) - Name of the Neo4j database

**Query Parameters:** None

**Headers:**
```http
X-API-Key: your-secret-api-key
```

### Response

#### Success (200 OK)

```json
98765
```

**Schema:**
```typescript
number  // Total relationship count
```

### Behavior

**Query:**
```cypher
MATCH ()-[r]->() RETURN count(r) as count
```

### Examples

#### Example 1: Get Edge Count

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/neo4j/graph/edges/count
```

**Response (200):**
```json
98765
```

---

## Testing Requirements

### Test Scenarios

**For GET /api/{database}/graph/nodes/{node_id}:**

1. ✅ **Get existing node returns 200**
   - Request valid node ID
   - Returns node with properties

2. ✅ **Non-existent node returns 404**
   - Request non-existent ID
   - Returns NODE_NOT_FOUND error

3. ✅ **Invalid node ID format returns 400**
   - Request with non-numeric ID
   - Returns INVALID_NODE_ID error

4. ✅ **Missing API key returns 403**
   - Request without X-API-Key
   - Returns auth error

**For POST /api/{database}/graph/nodes/expand:**

1. ✅ **Expand single node**
   - Expand one node
   - Returns node + neighbors + edges

2. ✅ **Expand multiple nodes**
   - Expand array of nodes
   - Returns combined subgraph

3. ✅ **Empty IDs array returns 422**
   - Send empty ids array
   - Returns validation error

4. ✅ **Node with no neighbors**
   - Expand isolated node
   - Returns just the node, no edges

5. ✅ **Limit parameter works**
   - Expand with limit=5
   - Returns max 5 neighbors

**For GET /api/{database}/graph/nodes/count:**

1. ✅ **Returns integer count**
   - Request node count
   - Returns number

2. ✅ **Count is accurate**
   - Compare with actual node count
   - Numbers match

**For GET /api/{database}/graph/edges/count:**

1. ✅ **Returns integer count**
   - Request edge count
   - Returns number

### Test Implementation

```python
def test_get_node_success(client, api_key, mock_neo4j):
    """Test getting node by ID."""
    mock_neo4j.execute_query.return_value = (
        [{"n": MockNode(id=123, labels=["Person"], props={"name": "Alice"})}],
        None,
        None
    )

    response = client.get(
        "/api/testdb/graph/nodes/123",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nodes"][0]["id"] == "123"
    assert data["nodes"][0]["data"]["properties"]["name"] == "Alice"

def test_get_node_not_found(client, api_key, mock_neo4j):
    """Test getting non-existent node."""
    mock_neo4j.execute_query.return_value = ([], None, None)

    response = client.get(
        "/api/testdb/graph/nodes/99999",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NODE_NOT_FOUND"

def test_expand_nodes(client, api_key, mock_neo4j):
    """Test expanding nodes."""
    mock_neo4j.execute_query.return_value = (
        [
            {
                "n": MockNode(id=123, labels=["Person"], props={"name": "Alice"}),
                "r": MockRelationship(id=789, type="KNOWS", source=123, target=456, props={}),
                "m": MockNode(id=456, labels=["Person"], props={"name": "Bob"})
            }
        ],
        None,
        None
    )

    response = client.post(
        "/api/testdb/graph/nodes/expand",
        headers={"X-API-Key": api_key},
        json={"ids": ["123"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1

def test_node_count(client, api_key, mock_neo4j):
    """Test getting node count."""
    mock_neo4j.execute_query.return_value = ([{"count": 42}], None, None)

    response = client.get(
        "/api/testdb/graph/nodes/count",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    assert response.json() == 42
```

---

## Future Enhancements

### 1. Filtered Expansion

Expand only specific relationship types or directions:

```json
{
  "ids": ["123"],
  "relationship_types": ["KNOWS", "WORKS_WITH"],
  "direction": "outgoing"
}
```

### 2. Depth Control

Expand multiple hops:

```json
{
  "ids": ["123"],
  "depth": 2  // 2-hop neighborhood
}
```

### 3. Property Filtering

Expand only to nodes matching criteria:

```json
{
  "ids": ["123"],
  "node_filter": {
    "labels": ["Person"],
    "properties": {"age": {">": 25}}
  }
}
```

### 4. Cached Counts

Cache node/edge counts to avoid expensive queries:

```json
{
  "count": 15247,
  "cached_at": "2025-11-03T12:00:00Z",
  "cache_ttl_seconds": 3600
}
```
