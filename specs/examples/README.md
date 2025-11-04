# API Examples

Concrete request and response examples for all API endpoints.

## Organization

Examples are organized by endpoint:

### Health & Metadata
- **health-check-success.json** - Healthy service response
- **health-check-failure.json** - Unhealthy service response
- **databases-list.json** - List of available databases

### Search
- **search-node-request.json** - Search for nodes
- **search-node-response.json** - Node search results
- **search-edge-request.json** - Search for relationships
- **search-edge-response.json** - Edge search results

### Query Execution
- **query-request-simple.json** - Simple MATCH query
- **query-request-parameterized.json** - Query with parameters
- **query-response-graph.json** - Query returning nodes and edges
- **query-response-scalar.json** - Query returning scalar values

### Node Operations
- **node-get-response.json** - Get node by ID
- **node-expand-request.json** - Expand node neighborhood
- **node-expand-response.json** - Expanded subgraph
- **node-count-response.json** - Node count

### Schema
- **schema-node-types.json** - List of node labels
- **schema-edge-types.json** - List of relationship types

### Errors
- **error-missing-api-key.json** - 403 Missing authentication
- **error-invalid-api-key.json** - 403 Invalid API key
- **error-write-forbidden.json** - 403 Write operation blocked
- **error-node-not-found.json** - 404 Node not found
- **error-database-not-found.json** - 404 Database not found
- **error-validation-error.json** - 422 Validation error
- **error-query-syntax.json** - 400 Invalid Cypher syntax
- **error-query-timeout.json** - 504 Query timeout
- **error-server-error.json** - 500 Internal error

## Usage

### For Testing
```bash
# Use as test fixtures
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d @specs/examples/query-request-simple.json \
  http://localhost/api/neo4j/graph/query
```

### For Documentation
Reference these examples in API documentation.

### For Mock Servers
Use these examples as mock responses for frontend development.

### For Integration Tests
Load these as expected responses in integration tests.
