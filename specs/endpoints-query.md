# Query Execution Endpoints Specification

## Overview

Execute Cypher queries against a specific Neo4j database with read-only enforcement.

---

## POST /api/{database}/graph/query

### Purpose
Execute a Cypher query and return matching nodes and relationships in Linkurious-compatible format.

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** POST

**URL Pattern:** `/api/{database}/graph/query`

**Path Parameters:**
- `database` (string, required) - Name of the Neo4j database to query

**Headers:**
```http
X-API-Key: your-secret-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "MATCH (p:Person)-[r:WORKS_FOR]->(c:Company) WHERE p.age > $age RETURN p, r, c LIMIT $limit",
  "parameters": {
    "age": 25,
    "limit": 10
  }
}
```

**Schema:**
```typescript
{
  query: string              // Cypher query (required)
  parameters?: object        // Query parameters (optional, default: {})
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
        "properties": {
          "name": "Alice Smith",
          "age": 30,
          "email": "alice@example.com"
        }
      }
    },
    {
      "id": "456",
      "data": {
        "categories": ["Company"],
        "properties": {
          "name": "Acme Corp",
          "founded": 1990
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
          "since": "2020-01-15",
          "role": "Engineer"
        }
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

**Schema:**
```typescript
{
  nodes: Array<{
    id: string
    data: {
      categories: string[]        // Node labels
      properties: object          // Node properties
    }
  }>
  edges: Array<{
    id: string
    source: string               // Source node ID
    target: string               // Target node ID
    data: {
      type: string               // Relationship type
      properties: object         // Relationship properties
    }
  }>
  truncatedByLimit: boolean      // Results limited by query LIMIT clause
  meta?: {
    query_type: string           // "r" (read) or "w" (write)
    records_returned: number
    execution_time_ms: number
  }
}
```

#### Write Operation Forbidden (403)

```json
{
  "error": {
    "code": "WRITE_OPERATION_FORBIDDEN",
    "message": "Write operations are not allowed. This API is read-only.",
    "details": {
      "query": "CREATE (n:Person {name: 'Bob'}) RETURN n",
      "forbidden_keyword": "CREATE",
      "allowed_operations": ["MATCH", "RETURN", "CALL db.*", "SHOW"]
    }
  }
}
```

#### Query Syntax Error (400)

```json
{
  "error": {
    "code": "QUERY_SYNTAX_ERROR",
    "message": "Invalid Cypher query syntax",
    "details": {
      "query": "MATCH (n R n",
      "neo4j_error": "Invalid input 'R': expected 'RETURN' (line 1, column 10)",
      "position": 10
    }
  }
}
```

#### Query Timeout (504)

```json
{
  "error": {
    "code": "QUERY_TIMEOUT",
    "message": "Query execution exceeded timeout limit",
    "details": {
      "timeout_seconds": 60,
      "query": "MATCH (n)-[*10..20]-(m) RETURN n, m"
    }
  }
}
```

### Behavior

#### 1. Query Validation (Read-Only Enforcement)

**Allowed Query Types:**
- `MATCH` - Pattern matching
- `RETURN` - Return results
- `WITH` - Query composition
- `WHERE` - Filtering
- `ORDER BY` - Sorting
- `LIMIT` / `SKIP` - Pagination
- `CALL db.*` - Database procedures (labels, relationshipTypes, etc.)
- `SHOW` - Show databases, indexes, etc.
- `UNWIND` - List expansion
- `OPTIONAL MATCH` - Optional patterns

**Forbidden Query Types:**
- `CREATE` - Create nodes/relationships
- `DELETE` / `DETACH DELETE` - Delete nodes/relationships
- `MERGE` - Create or match
- `SET` - Update properties
- `REMOVE` - Remove properties/labels
- `DROP` - Drop indexes/constraints
- `CREATE INDEX` / `CREATE CONSTRAINT` - Schema modifications

**Validation Logic:**
```python
FORBIDDEN_KEYWORDS = ["CREATE", "DELETE", "MERGE", "SET", "REMOVE", "DROP"]
ALLOWED_PREFIXES = ["MATCH", "RETURN", "CALL db.", "SHOW", "WITH", "OPTIONAL MATCH", "UNWIND"]

def is_read_only_query(query: str) -> bool:
    query_upper = query.strip().upper()

    # Check for forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query_upper:
            return False

    # Check starts with allowed prefix
    return any(query_upper.startswith(prefix) for prefix in ALLOWED_PREFIXES)
```

#### 2. Query Execution

1. Validate query is read-only
2. Execute query with parameters using Neo4j driver
3. Set routing to read replicas (`RoutingControl.READ`)
4. Apply 60-second timeout
5. Extract nodes and relationships from results
6. Format response in Linkurious-compatible structure

#### 3. Result Processing

**Extract Nodes:**
- Iterate through query results
- Find all `Node` objects
- Deduplicate by node ID
- Format as `{id, data: {categories, properties}}`

**Extract Relationships:**
- Find all `Relationship` objects
- Include source and target node IDs
- Format as `{id, source, target, data: {type, properties}}`

**Handle Scalars:**
- If query returns only scalars (numbers, strings), wrap in meta
- Future: Support scalar-only responses

### Performance Considerations

- **Timeout:** 60 seconds (configurable)
- **Result Limit:** Recommend LIMIT clause in query
- **Connection Pooling:** Driver maintains pool of connections
- **Read Replicas:** Queries routed to read replicas when available

### Use Cases

#### 1. Simple Node Query

**Request:**
```json
{
  "query": "MATCH (p:Person) RETURN p LIMIT 10"
}
```

**Response:**
```json
{
  "nodes": [
    {"id": "1", "data": {"categories": ["Person"], "properties": {"name": "Alice"}}}
  ],
  "edges": [],
  "truncatedByLimit": false
}
```

#### 2. Pattern Query with Relationships

**Request:**
```json
{
  "query": "MATCH (p:Person)-[r:KNOWS]->(f:Person) WHERE p.name = $name RETURN p, r, f",
  "parameters": {"name": "Alice"}
}
```

**Response:**
```json
{
  "nodes": [
    {"id": "1", "data": {"categories": ["Person"], "properties": {"name": "Alice"}}},
    {"id": "2", "data": {"categories": ["Person"], "properties": {"name": "Bob"}}}
  ],
  "edges": [
    {"id": "10", "source": "1", "target": "2", "data": {"type": "KNOWS", "properties": {"since": "2020"}}}
  ],
  "truncatedByLimit": false
}
```

#### 3. Aggregation Query

**Request:**
```json
{
  "query": "MATCH (p:Person) RETURN count(p) as total"
}
```

**Response:**
```json
{
  "nodes": [],
  "edges": [],
  "truncatedByLimit": false,
  "meta": {
    "scalar_result": {"total": 150}
  }
}
```

### Examples

#### Example 1: Successful Query

**Request:**
```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (p:Person) WHERE p.age > $age RETURN p LIMIT $limit",
    "parameters": {"age": 25, "limit": 5}
  }' \
  http://localhost/api/neo4j/graph/query
```

**Response (200):**
```json
{
  "nodes": [
    {"id": "123", "data": {"categories": ["Person"], "properties": {"name": "Alice", "age": 30}}}
  ],
  "edges": [],
  "truncatedByLimit": false
}
```

#### Example 2: Write Operation Blocked

**Request:**
```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CREATE (p:Person {name: 'Charlie'}) RETURN p"
  }' \
  http://localhost/api/neo4j/graph/query
```

**Response (403):**
```json
{
  "error": {
    "code": "WRITE_OPERATION_FORBIDDEN",
    "message": "Write operations are not allowed. This API is read-only.",
    "details": {
      "query": "CREATE (p:Person {name: 'Charlie'}) RETURN p",
      "forbidden_keyword": "CREATE"
    }
  }
}
```

#### Example 3: Syntax Error

**Request:**
```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (n R n"
  }' \
  http://localhost/api/neo4j/graph/query
```

**Response (400):**
```json
{
  "error": {
    "code": "QUERY_SYNTAX_ERROR",
    "message": "Invalid Cypher query syntax",
    "details": {
      "query": "MATCH (n R n",
      "neo4j_error": "Invalid input 'R'"
    }
  }
}
```

---

## Testing Requirements

### Test Scenarios

1. ✅ **Execute read query successfully**
   - Send valid MATCH query
   - Returns 200 with nodes and edges
   - Results match query

2. ✅ **Parameterized queries work**
   - Send query with parameters
   - Parameters correctly substituted
   - Results match expected

3. ✅ **Write operations are blocked**
   - Send CREATE query → 403
   - Send DELETE query → 403
   - Send MERGE query → 403
   - Send SET query → 403

4. ✅ **Syntax errors return 400**
   - Send invalid Cypher
   - Returns 400 with error details

5. ✅ **Query timeout returns 504**
   - Send very long-running query
   - Returns 504 after timeout

6. ✅ **Empty results return valid structure**
   - Query with no matches
   - Returns 200 with empty nodes/edges arrays

7. ✅ **Complex pattern queries**
   - Multi-hop relationships
   - Multiple node types
   - Correctly extracts all nodes and edges

8. ✅ **Database isolation**
   - Query database A
   - Results only from database A (not B)

### Test Implementation

```python
def test_execute_read_query(client, api_key, mock_neo4j):
    """Test successful read query execution."""
    mock_neo4j.execute_query.return_value = (
        [{"p": MockNode(id=1, labels=["Person"], props={"name": "Alice"})}],
        MockSummary(query_type="r"),
        ["p"]
    )

    response = client.post(
        "/api/testdb/graph/query",
        headers={"X-API-Key": api_key},
        json={"query": "MATCH (p:Person) RETURN p LIMIT 1"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["data"]["properties"]["name"] == "Alice"

def test_write_query_forbidden(client, api_key):
    """Test that CREATE queries are blocked."""
    response = client.post(
        "/api/testdb/graph/query",
        headers={"X-API-Key": api_key},
        json={"query": "CREATE (n:Person {name: 'Bad'}) RETURN n"}
    )

    assert response.status_code == 403
    error = response.json()["error"]
    assert error["code"] == "WRITE_OPERATION_FORBIDDEN"
    assert "CREATE" in error["details"]["forbidden_keyword"]

def test_query_with_parameters(client, api_key, mock_neo4j):
    """Test parameterized queries."""
    mock_neo4j.execute_query.return_value = ([], None, [])

    response = client.post(
        "/api/testdb/graph/query",
        headers={"X-API-Key": api_key},
        json={
            "query": "MATCH (p:Person) WHERE p.age > $age RETURN p",
            "parameters": {"age": 25}
        }
    )

    assert response.status_code == 200
    # Verify parameters were passed to Neo4j
    call_args = mock_neo4j.execute_query.call_args
    assert call_args[1]["age"] == 25
```

---

## Implementation Notes

### Neo4j Driver Code

```python
from neo4j import RoutingControl
from neo4j.exceptions import Neo4jError

@app.post("/api/{database}/graph/query")
async def execute_query(
    database: str,
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    # Validate read-only
    if not is_read_only_query(request.query):
        raise WriteOperationError(request.query)

    try:
        # Execute query
        records, summary, keys = driver.execute_query(
            request.query,
            parameters_=request.parameters or {},
            database_=database,
            routing_=RoutingControl.READ,
            timeout_=60.0  # 60 seconds
        )

        # Extract nodes and relationships
        nodes, edges = extract_graph_elements(records)

        return {
            "nodes": nodes,
            "edges": edges,
            "truncatedByLimit": False,
            "meta": {
                "query_type": summary.query_type,
                "records_returned": len(records),
                "execution_time_ms": summary.result_available_after
            }
        }

    except Neo4jError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "QUERY_SYNTAX_ERROR",
                "message": str(e),
                "details": {"query": request.query}
            }
        )
```

---

## Future Enhancements

### 1. Query Templates

Saved queries that users can execute by name:

```json
{
  "template": "find_person_by_name",
  "parameters": {"name": "Alice"}
}
```

### 2. Dry Run / Explain

```json
{
  "query": "MATCH (p:Person) RETURN p",
  "explain": true
}
```

Returns query plan instead of results.

### 3. Query Stats

```json
{
  "nodes": [...],
  "edges": [...],
  "stats": {
    "nodes_scanned": 1000,
    "relationships_scanned": 5000,
    "db_hits": 1500
  }
}
```

### 4. Streaming Results

For very large result sets, stream results instead of buffering all in memory.
