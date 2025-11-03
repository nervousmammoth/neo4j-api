# API Overview

**Version:** 1.0.0
**Base URL:** `/api/`
**Protocol:** HTTP/HTTPS
**Format:** JSON

## Purpose

Provide a Linkurious-compatible REST API for Neo4j Enterprise multi-database instances with:
- Read-only access to prevent accidental data modification
- Multi-database routing via URL path
- Simple API key authentication
- Auto-generated OpenAPI documentation

## Target Users

- Developers replacing Linkurious Enterprise API
- Frontend applications querying Neo4j databases
- Investigation tools accessing multiple isolated databases

## Design Principles

### 1. Linkurious Compatibility
Maintain URL structure and response format compatibility with Linkurious Enterprise API where possible to minimize migration effort.

### 2. Read-Only by Default
Only allow read operations (MATCH, RETURN, CALL db.*, SHOW) to prevent accidental data modification. Write operations blocked at API level.

### 3. Multi-Database Native
Support Neo4j 4.0+ multi-database feature with database name in URL path: `/api/{database}/...`

### 4. Simple Authentication
Start with API key authentication via `X-API-Key` header. Future: OAuth2/OIDC with Authentik.

### 5. Developer-Friendly
- Auto-generated OpenAPI/Swagger documentation
- Clear error messages
- Consistent response formats
- Type validation

## Architecture

```
Client Request
    ↓
Caddy Reverse Proxy (:80)
    ↓
FastAPI Application (localhost:8000)
    ↓
Neo4j Enterprise (:7687)
    ├── Database: neo4j
    ├── Database: system
    ├── Database: investigation_001
    └── Database: investigation_002
```

## URL Structure

### Base Pattern
```
/api/{database}/{resource}/{operation}
```

### Examples
```
GET  /api/neo4j/search/node/full
POST /api/neo4j/graph/query
GET  /api/neo4j/graph/nodes/123
POST /api/neo4j/graph/nodes/expand
GET  /api/neo4j/graph/schema/node/types
```

### Special Endpoints (No Database)
```
GET /api/health          # Health check
GET /api/databases       # List databases
GET /api/docs            # Swagger UI
GET /api/redoc           # ReDoc
```

## HTTP Methods

| Method | Purpose | Idempotent | Used For |
|--------|---------|------------|----------|
| GET | Retrieve resources | Yes | Search, get node, counts, schema |
| POST | Execute operations | No | Query execution, node expansion |
| PUT | Full update | Yes | Not used in v1 (read-only) |
| PATCH | Partial update | No | Not used in v1 (read-only) |
| DELETE | Remove resource | Yes | Not used in v1 (read-only) |

## Response Format

### Success Response
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-03T12:00:00Z",
    "database": "neo4j"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "QUERY_SYNTAX_ERROR",
    "message": "Invalid Cypher syntax",
    "details": {
      "query": "MATCH (n R n",
      "position": 10
    }
  }
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing authentication |
| 403 | Forbidden | Invalid API key or write operation attempted |
| 404 | Not Found | Database or resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Neo4j connection lost |

## Authentication

### API Key (Current)
```http
GET /api/neo4j/graph/nodes/123
X-API-Key: your-secret-api-key
```

### Public Endpoints (No Auth Required)
- `/api/health`
- `/api/databases`
- `/api/docs`
- `/api/redoc`

### Future: OAuth2/OIDC
- Integration with Authentik
- JWT bearer tokens
- Fine-grained permissions per database

## Rate Limiting

**Not implemented in v1.0.0**

Future considerations:
- Per API key: 100 requests/minute
- Per IP: 1000 requests/hour
- Header: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Pagination

**Not implemented in v1.0.0**

Use Cypher LIMIT clause:
```cypher
MATCH (n:Person) RETURN n LIMIT 100
```

Future considerations:
- Cursor-based pagination
- Parameters: `limit`, `offset`
- Response: `next_cursor`, `has_more`

## Versioning

**Current:** No version prefix (implies v1)

Future:
- URL versioning: `/api/v2/...`
- Header versioning: `Accept: application/vnd.api+json; version=2`

## CORS

**Not configured in v1.0.0**

If needed for browser access:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key"],
)
```

## Content Negotiation

### Request
```http
Content-Type: application/json
```

### Response
```http
Content-Type: application/json; charset=utf-8
```

**Future:** Support for other formats (CSV, XML) if needed.

## Compression

Caddy automatically handles gzip compression for responses > 1KB.

## Caching

**Not implemented in v1.0.0**

Future considerations:
- Cache-Control headers
- ETag support
- Redis caching layer for frequent queries

## Security Considerations

### Read-Only Enforcement
- Query validator blocks: CREATE, DELETE, MERGE, SET, REMOVE, DROP
- Only allows: MATCH, RETURN, CALL db.*, SHOW

### Input Validation
- All inputs validated via Pydantic models
- Parameterized queries prevent injection
- Database names validated against allowed list

### API Key Security
- Keys stored in environment variables
- Keys transmitted via headers (not URL)
- HTTPS recommended for production

### Database Isolation
- Each database accessed independently
- No cross-database queries in v1
- Future: Fine-grained permissions per database

## Performance Considerations

### Query Timeouts
- Default: 60 seconds
- Configurable per endpoint
- Returns 504 Gateway Timeout if exceeded

### Connection Pooling
- Neo4j driver maintains connection pool
- Default pool size: 50 connections
- Configurable via environment variables

### Result Limits
- Recommend LIMIT clause in queries
- Future: Enforce maximum result size

## Monitoring & Logging

### Health Checks
```
GET /api/health
```
Returns Neo4j connectivity status.

### Logs
- Request logs: Caddy access logs
- Application logs: stdout (journalctl)
- Query audit logs: Future enhancement

### Metrics
**Future:** Prometheus metrics endpoint
- Request count
- Request duration
- Error rate
- Database query time

## API Lifecycle

### Current Version: 1.0.0

**Stability:** Beta - API may change based on feedback

**Support:** Active development

**Breaking Changes:** Will be communicated via GitHub releases

## Related Documentation

- [Authentication Spec](./authentication.md)
- [Error Handling Spec](./error-handling.md)
- [Data Models](./data-models.md)
- [Endpoint Specifications](./endpoints-health.md)
