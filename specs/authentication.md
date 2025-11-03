# Authentication Specification

## Overview

Authentication mechanism for the Neo4j Multi-Database REST API.

**Version 1.0.0:** Simple API key authentication
**Future Versions:** OAuth2/OIDC with Authentik integration

---

## API Key Authentication (v1.0.0)

### Mechanism

API keys are passed via HTTP header `X-API-Key`.

### Configuration

API key stored in environment variable:
```bash
API_KEY=your-secret-key-here
```

### Request Format

```http
GET /api/neo4j/graph/nodes/123
X-API-Key: your-secret-key-here
```

### Validation Process

1. Extract `X-API-Key` header from request
2. Compare with configured API key (exact match)
3. If match: Allow request
4. If no match or missing: Return 403 Forbidden

### Protected Endpoints

**Requires Authentication:**
- All `/api/{database}/...` endpoints
  - Search: `/api/{database}/search/**`
  - Query: `/api/{database}/graph/query`
  - Nodes: `/api/{database}/graph/nodes/**`
  - Schema: `/api/{database}/graph/schema/**`

**Public (No Authentication):**
- `/api/health`
- `/api/databases`
- `/api/docs`
- `/api/redoc`
- `/api/openapi.json`

### Error Responses

#### Missing API Key

**Status:** 403 Forbidden

```json
{
  "error": {
    "code": "MISSING_API_KEY",
    "message": "API key is required",
    "details": {
      "header": "X-API-Key"
    }
  }
}
```

#### Invalid API Key

**Status:** 403 Forbidden

```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "Invalid API key provided"
  }
}
```

### Security Considerations

**✅ Do:**
- Use HTTPS in production (prevents key interception)
- Store keys in environment variables (not in code)
- Use strong, random keys (min 32 characters)
- Rotate keys periodically
- Log failed authentication attempts

**❌ Don't:**
- Pass API key in URL query parameters
- Commit API keys to Git
- Share API keys between environments
- Use predictable API keys

### Key Generation

```bash
# Generate secure random API key
openssl rand -base64 32
```

Example output:
```
7xK9mP3nQ5vT2wY8bL6eR4cJ1hU0fM5sA7dG9tN3pW8=
```

### Multiple API Keys (Future)

**Not implemented in v1.0.0**

Future support for:
- Multiple API keys per user
- API key rotation without downtime
- API key expiration
- Key-specific permissions

---

## OAuth2/OIDC with Authentik (Future)

### Planned Implementation

**Phase 1: Basic OIDC**
- Users authenticate via Authentik
- Redirect flow for user login
- JWT tokens for API access

**Phase 2: LDAP Integration**
- Authentik syncs with Active Directory
- Corporate credentials work automatically
- Group mappings

**Phase 3: SAML Federation**
- Enterprise SSO integration
- Single sign-on from corporate portal

### JWT Token Format (Planned)

```http
GET /api/neo4j/graph/nodes/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Token payload:
```json
{
  "sub": "user123",
  "email": "user@example.com",
  "groups": ["investigators", "admins"],
  "databases": ["investigation_001", "investigation_002"],
  "exp": 1699999999
}
```

### Permission Model (Planned)

```typescript
{
  user_id: string
  databases: Array<{
    name: string
    permissions: ["read"] | ["read", "write"]
  }>
  groups: string[]
}
```

---

## Implementation Guide

### FastAPI Dependency

```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate API key from request header."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key is required"
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return api_key
```

### Usage in Endpoints

```python
from fastapi import Depends
from app.dependencies import verify_api_key

@app.get("/api/{database}/graph/nodes/{node_id}")
async def get_node(
    database: str,
    node_id: str,
    api_key: str = Depends(verify_api_key)  # Require auth
):
    # Endpoint implementation
    pass
```

### Public Endpoints

```python
@app.get("/api/health")
async def health_check():
    # No Depends(verify_api_key) - public endpoint
    pass
```

---

## Testing

### Test Cases

**Required Tests:**

1. ✅ **Valid API key allows access**
   - Provide correct API key
   - Expect 200 OK response

2. ✅ **Missing API key returns 403**
   - Omit X-API-Key header
   - Expect 403 Forbidden

3. ✅ **Invalid API key returns 403**
   - Provide wrong API key
   - Expect 403 Forbidden

4. ✅ **Public endpoints don't require auth**
   - Access /api/health without key
   - Expect 200 OK (not 403)

5. ✅ **Case-sensitive key validation**
   - Provide key with wrong case
   - Expect 403 Forbidden

6. ✅ **Empty API key returns 403**
   - Provide X-API-Key: ""
   - Expect 403 Forbidden

### Test Implementation

```python
def test_valid_api_key_allows_access(client, api_key):
    response = client.get(
        "/api/neo4j/graph/nodes/count",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200

def test_missing_api_key_returns_403(client):
    response = client.get("/api/neo4j/graph/nodes/count")
    assert response.status_code == 403
    assert "API key" in response.json()["error"]["message"]

def test_invalid_api_key_returns_403(client):
    response = client.get(
        "/api/neo4j/graph/nodes/count",
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 403

def test_public_endpoints_no_auth(client):
    response = client.get("/api/health")
    assert response.status_code != 403  # Should work without auth
```

---

## Client Integration Examples

### cURL

```bash
# Set API key as environment variable
export API_KEY="your-secret-key"

# Use in requests
curl -H "X-API-Key: $API_KEY" http://localhost/api/neo4j/graph/nodes/123
```

### Python (requests)

```python
import requests

API_KEY = "your-secret-key"
BASE_URL = "http://localhost/api"

headers = {"X-API-Key": API_KEY}

# Make authenticated request
response = requests.get(
    f"{BASE_URL}/neo4j/graph/nodes/123",
    headers=headers
)
```

### JavaScript (fetch)

```javascript
const API_KEY = 'your-secret-key';
const BASE_URL = 'http://localhost/api';

async function getNode(database, nodeId) {
  const response = await fetch(
    `${BASE_URL}/${database}/graph/nodes/${nodeId}`,
    {
      headers: {
        'X-API-Key': API_KEY
      }
    }
  );
  return response.json();
}
```

### JavaScript (axios)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost/api',
  headers: {
    'X-API-Key': 'your-secret-key'
  }
});

// Use the configured client
const response = await api.get('/neo4j/graph/nodes/123');
```

---

## Migration Path

### Current State (v1.0.0)
```
Single API Key → All Endpoints
```

### Phase 2 (Authentik OIDC)
```
User Login → Authentik → JWT Token → API
```

### Phase 3 (Fine-Grained Permissions)
```
User + Groups → Authentik → JWT with Claims → API → Database Permissions
```

---

## OpenAPI Security Scheme

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for authentication

security:
  - ApiKeyAuth: []  # Applied globally

paths:
  /api/health:
    get:
      security: []  # Override: no auth required
```
