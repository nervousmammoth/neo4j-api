# Error Handling Specification

## Overview

Consistent error response format and error codes for the Neo4j Multi-Database REST API.

---

## Error Response Format

All errors follow this consistent structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Optional additional context
    }
  }
}
```

**Schema:**
```typescript
{
  error: {
    code: string           // Machine-readable error code
    message: string        // Human-readable description
    details?: object       // Optional additional information
  }
}
```

---

## HTTP Status Codes

| Code | Name | Usage |
|------|------|-------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing authentication (not used in v1) |
| 403 | Forbidden | Invalid API key or permission denied |
| 404 | Not Found | Database or resource not found |
| 422 | Unprocessable Entity | Request validation failed |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Neo4j connection failed |
| 504 | Gateway Timeout | Query exceeded timeout |

---

## Error Codes & Scenarios

### Authentication Errors (403)

#### MISSING_API_KEY

**When:** No X-API-Key header provided

**Response:**
```json
{
  "error": {
    "code": "MISSING_API_KEY",
    "message": "API key is required for this endpoint",
    "details": {
      "header": "X-API-Key"
    }
  }
}
```

#### INVALID_API_KEY

**When:** Provided API key doesn't match

**Response:**
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid"
  }
}
```

---

### Database Errors (404, 503)

#### DATABASE_NOT_FOUND

**When:** Requested database doesn't exist

**HTTP Status:** 404

**Response:**
```json
{
  "error": {
    "code": "DATABASE_NOT_FOUND",
    "message": "Database 'nonexistent_db' not found",
    "details": {
      "database": "nonexistent_db",
      "available_databases": ["neo4j", "system"]
    }
  }
}
```

#### NEO4J_CONNECTION_ERROR

**When:** Cannot connect to Neo4j

**HTTP Status:** 503

**Response:**
```json
{
  "error": {
    "code": "NEO4J_CONNECTION_ERROR",
    "message": "Failed to connect to Neo4j database",
    "details": {
      "neo4j_uri": "bolt://localhost:7687",
      "error": "Connection refused"
    }
  }
}
```

---

### Query Errors (400, 403, 500, 504)

#### WRITE_OPERATION_FORBIDDEN

**When:** Attempt to execute write query (CREATE, DELETE, etc.)

**HTTP Status:** 403

**Response:**
```json
{
  "error": {
    "code": "WRITE_OPERATION_FORBIDDEN",
    "message": "Write operations are not allowed. This API is read-only.",
    "details": {
      "query": "CREATE (n:Person {name: 'John'}) RETURN n",
      "forbidden_keyword": "CREATE",
      "allowed_operations": ["MATCH", "RETURN", "CALL db.*", "SHOW"]
    }
  }
}
```

#### QUERY_SYNTAX_ERROR

**When:** Invalid Cypher syntax

**HTTP Status:** 400

**Response:**
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

#### QUERY_TIMEOUT

**When:** Query execution exceeds timeout

**HTTP Status:** 504

**Response:**
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

#### QUERY_EXECUTION_ERROR

**When:** Query executes but fails (e.g., division by zero, type mismatch)

**HTTP Status:** 500

**Response:**
```json
{
  "error": {
    "code": "QUERY_EXECUTION_ERROR",
    "message": "Query execution failed",
    "details": {
      "query": "MATCH (n) RETURN n.age / 0",
      "neo4j_error": "/ by zero"
    }
  }
}
```

---

### Validation Errors (422)

#### VALIDATION_ERROR

**When:** Request doesn't match expected schema (Pydantic validation)

**HTTP Status:** 422

**Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "query",
          "message": "Field required",
          "type": "missing"
        },
        {
          "field": "fuzziness",
          "message": "Value must be between 0 and 1",
          "type": "value_error"
        }
      ]
    }
  }
}
```

---

### Resource Errors (404)

#### NODE_NOT_FOUND

**When:** Requested node doesn't exist

**HTTP Status:** 404

**Response:**
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

#### RELATIONSHIP_NOT_FOUND

**When:** Requested relationship doesn't exist

**HTTP Status:** 404

**Response:**
```json
{
  "error": {
    "code": "RELATIONSHIP_NOT_FOUND",
    "message": "Relationship with ID '67890' not found",
    "details": {
      "relationship_id": "67890",
      "database": "neo4j"
    }
  }
}
```

---

### Server Errors (500)

#### INTERNAL_SERVER_ERROR

**When:** Unexpected server error

**HTTP Status:** 500

**Response:**
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "error_id": "uuid-12345",
      "timestamp": "2025-11-03T12:00:00Z"
    }
  }
}
```

**Note:** Include `error_id` for log correlation, but don't expose stack traces in production.

---

## Error Handling Best Practices

### For API Implementers

1. **Always return error object**
   ```python
   # Good
   return JSONResponse(
       status_code=404,
       content={"error": {"code": "NODE_NOT_FOUND", "message": "..."}}
   )

   # Bad
   return {"message": "Not found"}  # Inconsistent format
   ```

2. **Include relevant context**
   ```python
   # Good - includes query that caused error
   {"error": {"code": "...", "details": {"query": "MATCH..."}}}

   # Bad - no context
   {"error": {"code": "...", "message": "Query failed"}}
   ```

3. **Don't expose sensitive information**
   ```python
   # Good
   {"error": {"message": "Database connection failed"}}

   # Bad - exposes credentials
   {"error": {"message": "Failed: user neo4j password abc123 ..."}}
   ```

4. **Log errors server-side**
   ```python
   logger.error(f"Query failed: {query}", exc_info=True, extra={
       "user": user_id,
       "database": database,
       "query": query
   })
   ```

### For API Consumers

1. **Always check status code first**
   ```python
   if response.status_code != 200:
       error = response.json()["error"]
       handle_error(error["code"], error["message"])
   ```

2. **Match on error codes, not messages**
   ```python
   # Good
   if error["code"] == "WRITE_OPERATION_FORBIDDEN":
       ...

   # Bad - messages may change
   if "write" in error["message"]:
       ...
   ```

3. **Handle unknown errors gracefully**
   ```python
   try:
       response = api.get(...)
   except HTTPError as e:
       if e.response.status_code == 503:
           show_message("Service temporarily unavailable")
       else:
           show_message("An error occurred. Please try again.")
   ```

---

## Implementation Guidelines

### FastAPI Exception Handlers

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from neo4j.exceptions import Neo4jError, ServiceUnavailable

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail
            }
        }
    )

@app.exception_handler(ServiceUnavailable)
async def neo4j_unavailable_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "NEO4J_CONNECTION_ERROR",
                "message": "Cannot connect to Neo4j",
                "details": {"neo4j_error": str(exc)}
            }
        }
    )

@app.exception_handler(Neo4jError)
async def neo4j_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "QUERY_EXECUTION_ERROR",
                "message": "Query execution failed",
                "details": {"neo4j_error": str(exc)}
            }
        }
    )
```

### Custom Exceptions

```python
class WriteOperationError(HTTPException):
    def __init__(self, query: str, keyword: str):
        super().__init__(
            status_code=403,
            detail={
                "code": "WRITE_OPERATION_FORBIDDEN",
                "message": "Write operations are not allowed",
                "details": {
                    "query": query,
                    "forbidden_keyword": keyword
                }
            }
        )

class DatabaseNotFoundError(HTTPException):
    def __init__(self, database: str):
        super().__init__(
            status_code=404,
            detail={
                "code": "DATABASE_NOT_FOUND",
                "message": f"Database '{database}' not found",
                "details": {"database": database}
            }
        )
```

---

## Testing Requirements

### Test Cases

1. ✅ **Each error code has a test**
   - Trigger error condition
   - Verify status code
   - Verify error structure
   - Verify error code and message

2. ✅ **Error response format consistency**
   - All errors have `error` object
   - All have `code` and `message`
   - `details` is object when present

3. ✅ **Status code correctness**
   - Auth errors → 403
   - Not found → 404
   - Validation → 422
   - Server errors → 500
   - Neo4j down → 503

4. ✅ **Error messages are helpful**
   - Clear explanation of problem
   - Guidance on how to fix
   - No sensitive information exposed

### Example Test

```python
def test_write_operation_forbidden(client, api_key):
    response = client.post(
        "/api/neo4j/graph/query",
        headers={"X-API-Key": api_key},
        json={"query": "CREATE (n:Person) RETURN n"}
    )

    assert response.status_code == 403

    error = response.json()["error"]
    assert error["code"] == "WRITE_OPERATION_FORBIDDEN"
    assert "write" in error["message"].lower()
    assert error["details"]["forbidden_keyword"] == "CREATE"
```

---

## Future Enhancements

### 1. Structured Error Codes

```json
{
  "error": {
    "code": "NEO4J.CONNECTION.REFUSED",
    "category": "infrastructure",
    "severity": "critical",
    "message": "..."
  }
}
```

### 2. Localization

```json
{
  "error": {
    "code": "NODE_NOT_FOUND",
    "message": "Node not found",
    "message_localized": {
      "en": "Node not found",
      "de": "Knoten nicht gefunden",
      "fr": "Nœud non trouvé"
    }
  }
}
```

### 3. Error Recovery Suggestions

```json
{
  "error": {
    "code": "QUERY_TIMEOUT",
    "message": "Query timed out",
    "suggestions": [
      "Add LIMIT clause to reduce result size",
      "Simplify query complexity",
      "Contact support if issue persists"
    ]
  }
}
```
