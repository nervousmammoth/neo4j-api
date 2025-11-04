# Search Endpoints Specification

## Overview

Search for nodes or edges within a specific database using full-text search with fuzzy matching.

---

## GET /api/{database}/search/node/full

### Purpose
Search for nodes where at least one property matches the search query. Returns a subgraph of matching nodes and edges between them (Linkurious-compatible).

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** GET

**URL Pattern:** `/api/{database}/search/node/full`

**Path Parameters:**
- `database` (string, required) - Name of the Neo4j database to search

**Query Parameters:**
- `q` (string, required) - Search query string
  - Min length: 1 character
  - Example: `"Alice"`, `"fraud investigation"`
- `fuzziness` (float, optional) - Fuzzy matching tolerance
  - Range: 0.0 to 1.0
  - Default: 0.7
  - 0.0 = exact match only
  - 1.0 = maximum fuzziness (tolerates more typos)
- `size` (integer, optional) - Maximum number of results
  - Default: 20
  - Range: 1 to 1000
- `from` (integer, optional) - Offset for pagination
  - Default: 0
  - Min: 0

**Headers:**
```http
X-API-Key: your-secret-api-key
```

**Request Body:** None

### Response

#### Success (200 OK)

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
        "age": 30,
        "email": "alice@example.com",
        "city": "New York"
      }
    },
    {
      "id": "456",
      "labels": ["Person", "Employee"],
      "properties": {
        "name": "Alice Johnson",
        "age": 28,
        "department": "Engineering"
      }
    }
  ]
}
```

**Schema:**
```typescript
{
  type: "node" | "edge"
  totalHits?: number           // Total matching items (if known)
  moreResults?: boolean        // True if more results available
  results: Array<{
    id: string                 // Node ID (as string)
    labels: string[]           // Node labels
    properties: object         // All node properties
  }>
}
```

#### Database Not Found (404)

```json
{
  "error": {
    "code": "DATABASE_NOT_FOUND",
    "message": "Database 'nonexistent' not found",
    "details": {
      "database": "nonexistent"
    }
  }
}
```

#### Validation Error (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "q",
          "message": "Field required",
          "type": "missing"
        }
      ]
    }
  }
}
```

#### Authentication Error (403)

See [authentication.md](./authentication.md) for auth error formats.

### Behavior

1. **Query Parsing**
   - Convert search query to Cypher pattern
   - Apply fuzzy matching if fuzziness > 0

2. **Search Execution**
   - Search across all node properties
   - Case-insensitive matching
   - Support for partial matches

3. **Result Formatting**
   - Return nodes with all properties
   - Include node labels
   - Convert Neo4j node IDs to strings

4. **Pagination**
   - Apply `from` offset
   - Limit results to `size` parameter
   - Set `moreResults` flag if more available

### Implementation Notes

**Basic Search Query (v1.0.0):**
```cypher
MATCH (n)
WHERE ANY(prop IN keys(n) WHERE toString(n[prop]) CONTAINS $q)
RETURN n
LIMIT $size
```

**Future Enhancement (with Neo4j full-text index):**
```cypher
CALL db.index.fulltext.queryNodes('node_index', $q)
YIELD node, score
RETURN node
ORDER BY score DESC
LIMIT $size
```

### Performance Considerations

- **Expected Response Time:** < 2 seconds for most queries
- **Timeout:** 30 seconds
- **Result Limit:** Max 1000 nodes
- **Indexing:** Consider full-text indexes for large databases

### Use Cases

1. **Find Person by Name**
   ```
   GET /api/neo4j/search/node/full?q=Alice
   ```

2. **Fuzzy Search (typo-tolerant)**
   ```
   GET /api/neo4j/search/node/full?q=Alise&fuzziness=0.8
   ```

3. **Search with Pagination**
   ```
   GET /api/neo4j/search/node/full?q=Smith&size=50&from=100
   ```

### Examples

#### Example 1: Search by Name

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost/api/neo4j/search/node/full?q=Alice&fuzziness=0.7"
```

**Response (200):**
```json
{
  "type": "node",
  "totalHits": 2,
  "moreResults": false,
  "results": [
    {
      "id": "123",
      "labels": ["Person"],
      "properties": {
        "name": "Alice Smith",
        "age": 30
      }
    },
    {
      "id": "456",
      "labels": ["Person"],
      "properties": {
        "name": "Alice Johnson",
        "age": 28
      }
    }
  ]
}
```

#### Example 2: No Results

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost/api/neo4j/search/node/full?q=NonexistentPerson"
```

**Response (200):**
```json
{
  "type": "node",
  "totalHits": 0,
  "moreResults": false,
  "results": []
}
```

#### Example 3: Invalid Database

**Request:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost/api/invalid_db/search/node/full?q=test"
```

**Response (404):**
```json
{
  "error": {
    "code": "DATABASE_NOT_FOUND",
    "message": "Database 'invalid_db' not found",
    "details": {
      "database": "invalid_db"
    }
  }
}
```

---

## GET /api/{database}/search/edge/full

### Purpose
Search for relationships (edges) where at least one property matches the search query.

### Authentication
**Required:** API Key via `X-API-Key` header

### Request

**HTTP Method:** GET

**URL Pattern:** `/api/{database}/search/edge/full`

**Path Parameters:**
- `database` (string, required) - Name of the Neo4j database

**Query Parameters:**
Same as node search:
- `q` (string, required) - Search query
- `fuzziness` (float, optional) - Fuzzy matching (0-1)
- `size` (integer, optional) - Max results (default: 20)
- `from` (integer, optional) - Offset (default: 0)

**Headers:**
```http
X-API-Key: your-secret-api-key
```

### Response

#### Success (200 OK)

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
        "since": "2020-01-15",
        "role": "Engineer"
      }
    }
  ]
}
```

**Schema:**
```typescript
{
  type: "edge"
  totalHits?: number
  moreResults?: boolean
  results: Array<{
    id: string              // Relationship ID
    type: string            // Relationship type
    source: string          // Source node ID
    target: string          // Target node ID
    properties: object      // Relationship properties
  }>
}
```

### Behavior

Similar to node search, but searches relationship properties instead.

**Search Query:**
```cypher
MATCH ()-[r]-()
WHERE ANY(prop IN keys(r) WHERE toString(r[prop]) CONTAINS $q)
RETURN r, startNode(r), endNode(r)
LIMIT $size
```

---

## Testing Requirements

### Test Scenarios

**For Node Search:**

1. ✅ **Successful search returns results**
   - Search query matches nodes
   - Returns 200 with results array
   - Results contain id, labels, properties

2. ✅ **Empty search returns empty array**
   - No nodes match query
   - Returns 200 with empty results
   - totalHits is 0

3. ✅ **Fuzzy search tolerates typos**
   - Search "Alise" with fuzziness=0.8
   - Finds "Alice"
   - Returns matching results

4. ✅ **Pagination works correctly**
   - Request with from=10, size=5
   - Returns 5 results starting at offset 10
   - moreResults flag set correctly

5. ✅ **Invalid database returns 404**
   - Request nonexistent database
   - Returns 404 DATABASE_NOT_FOUND

6. ✅ **Missing query parameter returns 422**
   - Omit 'q' parameter
   - Returns 422 validation error

7. ✅ **Case-insensitive search**
   - Search "ALICE" finds "alice"
   - Search "alice" finds "ALICE"

8. ✅ **Missing API key returns 403**
   - Omit X-API-Key header
   - Returns 403 MISSING_API_KEY

**For Edge Search:**

1. ✅ **Search relationships by property**
   - Search query matches edge properties
   - Returns edges with source/target

2. ✅ **Empty edge search**
   - No relationships match
   - Returns empty results

### Test Implementation

```python
def test_search_nodes_success(client, api_key, mock_neo4j):
    """Test successful node search."""
    mock_neo4j.execute_query.return_value = (
        [
            {"n": MockNode(id=123, labels=["Person"], props={"name": "Alice"})}
        ],
        None,
        None
    )

    response = client.get(
        "/api/testdb/search/node/full?q=Alice&fuzziness=0.7",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "node"
    assert len(data["results"]) == 1
    assert data["results"][0]["properties"]["name"] == "Alice"

def test_search_empty_results(client, api_key, mock_neo4j):
    """Test search with no results."""
    mock_neo4j.execute_query.return_value = ([], None, None)

    response = client.get(
        "/api/testdb/search/node/full?q=Nonexistent",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["totalHits"] == 0
    assert data["results"] == []

def test_search_missing_query_param(client, api_key):
    """Test search without required 'q' parameter."""
    response = client.get(
        "/api/testdb/search/node/full",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 422
    assert "q" in response.json()["error"]["details"]["errors"][0]["field"]

def test_search_invalid_database(client, api_key):
    """Test search on nonexistent database."""
    response = client.get(
        "/api/nonexistent/search/node/full?q=test",
        headers={"X-API-Key": api_key}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DATABASE_NOT_FOUND"
```

---

## Future Enhancements

### 1. Advanced Filters

```
GET /api/{database}/search/node/full?q=Alice&labels=Person&property=age>25
```

Support filtering by:
- Node labels
- Property value ranges
- Date ranges

### 2. Highlight Matches

```json
{
  "results": [
    {
      "id": "123",
      "properties": {
        "name": "Alice Smith"
      },
      "highlights": {
        "name": "<em>Alice</em> Smith"
      }
    }
  ]
}
```

### 3. Full-Text Index Integration

Use Neo4j full-text indexes for better performance and relevance scoring.

### 4. Faceted Search

```json
{
  "results": [...],
  "facets": {
    "labels": {
      "Person": 10,
      "Company": 5
    },
    "age": {
      "20-30": 5,
      "30-40": 3
    }
  }
}
```

### 5. Query Suggestions

```json
{
  "results": [],
  "suggestions": [
    "Did you mean: Alicia?",
    "Did you mean: Alexander?"
  ]
}
```
