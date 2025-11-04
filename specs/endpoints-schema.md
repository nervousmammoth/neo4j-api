# Schema Endpoints Specification

## Overview

Endpoints for retrieving database schema information (node labels and relationship types).

---

## GET /api/{database}/graph/schema/node/types

### Purpose
Get all node labels (types) in the database.

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** GET

**URL Pattern:** `/api/{database}/graph/schema/node/types`

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
{
  "types": [
    "Person",
    "Company",
    "Product",
    "Order"
  ]
}
```

**Schema:**
```typescript
{
  types: string[]  // Array of node label names
}
```

**Alternative detailed format (future):**
```json
{
  "types": [
    {
      "name": "Person",
      "count": 1500,
      "properties": ["name", "age", "email"]
    },
    {
      "name": "Company",
      "count": 250,
      "properties": ["name", "founded", "industry"]
    }
  ]
}
```

#### Database Error (500)

```json
{
  "error": {
    "code": "QUERY_EXECUTION_ERROR",
    "message": "Failed to retrieve node labels",
    "details": {
      "database": "neo4j",
      "neo4j_error": "Permission denied"
    }
  }
}
```

### Behavior

1. **Query Node Labels**
   ```cypher
   CALL db.labels()
   ```

2. **Format Response**
   - Return array of label strings
   - Sort alphabetically (optional)

3. **Caching**
   - Schema changes infrequently
   - Consider caching for 5-10 minutes (future)

### Use Cases

#### 1. Database Discovery
Help users understand what types of entities exist in the database.

#### 2. Query Builder UI
Populate dropdown with available node types for visual query builder.

#### 3. Documentation
Auto-generate database schema documentation.

### Examples

#### Example 1: Get Node Types

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/neo4j/graph/schema/node/types
```

**Response (200):**
```json
{
  "types": ["Person", "Company", "Product", "Order", "Invoice"]
}
```

#### Example 2: Empty Database

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/emptydb/graph/schema/node/types
```

**Response (200):**
```json
{
  "types": []
}
```

---

## GET /api/{database}/graph/schema/edge/types

### Purpose
Get all relationship types in the database.

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** GET

**URL Pattern:** `/api/{database}/graph/schema/edge/types`

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
{
  "types": [
    "WORKS_FOR",
    "KNOWS",
    "MANAGES",
    "PURCHASED",
    "CONTAINS"
  ]
}
```

**Schema:**
```typescript
{
  types: string[]  // Array of relationship type names
}
```

**Alternative detailed format (future):**
```json
{
  "types": [
    {
      "name": "WORKS_FOR",
      "count": 5000,
      "properties": ["since", "role"],
      "source_labels": ["Person"],
      "target_labels": ["Company"]
    },
    {
      "name": "KNOWS",
      "count": 15000,
      "properties": ["since"],
      "source_labels": ["Person"],
      "target_labels": ["Person"]
    }
  ]
}
```

#### Database Error (500)

```json
{
  "error": {
    "code": "QUERY_EXECUTION_ERROR",
    "message": "Failed to retrieve relationship types",
    "details": {
      "database": "neo4j",
      "neo4j_error": "..."
    }
  }
}
```

### Behavior

1. **Query Relationship Types**
   ```cypher
   CALL db.relationshipTypes()
   ```

2. **Format Response**
   - Return array of type strings
   - Sort alphabetically (optional)

3. **Caching**
   - Schema changes infrequently
   - Consider caching for 5-10 minutes (future)

### Use Cases

#### 1. Relationship Discovery
Help users understand what types of connections exist.

#### 2. Query Builder UI
Populate dropdown with available relationship types.

#### 3. Graph Visualization
Configure different colors/styles for different relationship types.

### Examples

#### Example 1: Get Relationship Types

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/neo4j/graph/schema/edge/types
```

**Response (200):**
```json
{
  "types": [
    "WORKS_FOR",
    "KNOWS",
    "MANAGES",
    "FRIEND_OF",
    "PURCHASED"
  ]
}
```

#### Example 2: No Relationships

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  http://localhost/api/nodes_only_db/graph/schema/edge/types
```

**Response (200):**
```json
{
  "types": []
}
```

---

## GET /api/{database}/graph/schema (Future Enhancement)

### Purpose
Get complete schema including nodes, relationships, properties, and constraints.

**Not implemented in v1.0.0**

### Planned Response Format

```json
{
  "nodes": [
    {
      "label": "Person",
      "count": 1500,
      "properties": [
        {"name": "name", "type": "String", "required": true},
        {"name": "age", "type": "Integer", "required": false},
        {"name": "email", "type": "String", "required": false}
      ],
      "indexes": [
        {"on": "name", "type": "BTREE"},
        {"on": "email", "type": "UNIQUE"}
      ],
      "constraints": [
        {"on": "email", "type": "UNIQUE"}
      ]
    }
  ],
  "relationships": [
    {
      "type": "WORKS_FOR",
      "count": 5000,
      "source_labels": ["Person"],
      "target_labels": ["Company"],
      "properties": [
        {"name": "since", "type": "Date"},
        {"name": "role", "type": "String"}
      ]
    }
  ]
}
```

---

## Testing Requirements

### Test Scenarios

**For GET /api/{database}/graph/schema/node/types:**

1. ✅ **Returns array of node labels**
   - Database has multiple node types
   - Returns all labels in array

2. ✅ **Empty database returns empty array**
   - No nodes in database
   - Returns empty types array

3. ✅ **Response is valid JSON array**
   - All labels are strings
   - No duplicates

4. ✅ **Missing API key returns 403**
   - Request without auth
   - Returns auth error

5. ✅ **Database not found returns 404**
   - Request nonexistent database
   - Returns DATABASE_NOT_FOUND

**For GET /api/{database}/graph/schema/edge/types:**

1. ✅ **Returns array of relationship types**
   - Database has multiple relationship types
   - Returns all types in array

2. ✅ **No relationships returns empty array**
   - Database has nodes but no relationships
   - Returns empty types array

3. ✅ **Response is valid JSON array**
   - All types are strings
   - No duplicates

### Test Implementation

```python
def test_get_node_types(client, api_key, mock_neo4j):
    """Test getting node labels."""
    mock_neo4j.execute_query.return_value = (
        [{"label": "Person"}, {"label": "Company"}, {"label": "Product"}],
        None,
        None
    )

    response = client.get(
        "/api/testdb/graph/schema/node/types",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    assert len(data["types"]) == 3
    assert "Person" in data["types"]
    assert "Company" in data["types"]
    assert "Product" in data["types"]

def test_get_node_types_empty(client, api_key, mock_neo4j):
    """Test getting node labels from empty database."""
    mock_neo4j.execute_query.return_value = ([], None, None)

    response = client.get(
        "/api/emptydb/graph/schema/node/types",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    assert response.json() == {"types": []}

def test_get_edge_types(client, api_key, mock_neo4j):
    """Test getting relationship types."""
    mock_neo4j.execute_query.return_value = (
        [
            {"relationshipType": "WORKS_FOR"},
            {"relationshipType": "KNOWS"},
            {"relationshipType": "MANAGES"}
        ],
        None,
        None
    )

    response = client.get(
        "/api/testdb/graph/schema/edge/types",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    assert len(data["types"]) == 3
    assert "WORKS_FOR" in data["types"]

def test_get_schema_without_auth(client):
    """Test that schema endpoints require authentication."""
    response = client.get("/api/testdb/graph/schema/node/types")
    assert response.status_code == 403

    response = client.get("/api/testdb/graph/schema/edge/types")
    assert response.status_code == 403
```

---

## Implementation Notes

### Neo4j Driver Code

```python
@app.get("/api/{database}/graph/schema/node/types")
async def get_node_types(
    database: str,
    api_key: str = Depends(verify_api_key)
):
    """Get all node labels in the database."""
    try:
        records, _, _ = driver.execute_query(
            "CALL db.labels()",
            database_=database,
            routing_=RoutingControl.READ
        )

        labels = [record["label"] for record in records]
        return {"types": sorted(labels)}  # Optional: sort alphabetically

    except Neo4jError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "QUERY_EXECUTION_ERROR",
                "message": "Failed to retrieve node labels",
                "details": {"neo4j_error": str(e)}
            }
        )

@app.get("/api/{database}/graph/schema/edge/types")
async def get_edge_types(
    database: str,
    api_key: str = Depends(verify_api_key)
):
    """Get all relationship types in the database."""
    try:
        records, _, _ = driver.execute_query(
            "CALL db.relationshipTypes()",
            database_=database,
            routing_=RoutingControl.READ
        )

        types = [record["relationshipType"] for record in records]
        return {"types": sorted(types)}  # Optional: sort alphabetically

    except Neo4jError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "QUERY_EXECUTION_ERROR",
                "message": "Failed to retrieve relationship types",
                "details": {"neo4j_error": str(e)}
            }
        )
```

---

## Performance Considerations

- **Query Performance:** `CALL db.labels()` and `CALL db.relationshipTypes()` are fast (< 100ms)
- **Caching:** Schema changes rarely, consider caching results for 5-10 minutes
- **Sorting:** Optional alphabetical sorting improves UX but adds minimal overhead

---

## Future Enhancements

### 1. Property Schema

For each label/type, include available properties:

```json
{
  "types": [
    {
      "label": "Person",
      "properties": ["name", "age", "email", "city"]
    }
  ]
}
```

### 2. Constraints and Indexes

Include database constraints and indexes:

```json
{
  "types": [
    {
      "label": "Person",
      "constraints": [
        {"type": "UNIQUE", "properties": ["email"]},
        {"type": "NODE_KEY", "properties": ["id"]}
      ],
      "indexes": [
        {"type": "BTREE", "properties": ["name"]},
        {"type": "FULLTEXT", "properties": ["name", "bio"]}
      ]
    }
  ]
}
```

### 3. Node/Relationship Counts

Include counts for each type:

```json
{
  "types": [
    {"label": "Person", "count": 1500},
    {"label": "Company", "count": 250}
  ]
}
```

Query:
```cypher
MATCH (n:Person) RETURN count(n) as count
```

### 4. Sample Data

Provide sample node for each type:

```json
{
  "types": [
    {
      "label": "Person",
      "sample": {
        "name": "Alice Smith",
        "age": 30,
        "email": "alice@example.com"
      }
    }
  ]
}
```

### 5. Relationship Patterns

Show common source → relationship → target patterns:

```json
{
  "patterns": [
    {
      "source": "Person",
      "relationship": "WORKS_FOR",
      "target": "Company",
      "count": 5000
    }
  ]
}
```
