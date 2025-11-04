# Health & Metadata Endpoints

## Overview

Public endpoints for health checks and database discovery. No authentication required.

---

## GET /api/health

### Purpose
Check API and Neo4j connectivity status.

### Authentication
None required (public endpoint)

### Request

**HTTP Method:** GET

**URL:** `/api/health`

**Headers:** None required

**Query Parameters:** None

**Request Body:** None

### Response

#### Success (200 OK)

**When:** Neo4j is connected and responsive

```json
{
  "status": "healthy",
  "neo4j": "connected",
  "version": "1.0.0"
}
```

**Schema:**
```typescript
{
  status: "healthy" | "unhealthy"
  neo4j: "connected" | "disconnected"
  version: string
}
```

#### Service Unavailable (503)

**When:** Neo4j connection failed

```json
{
  "status": "unhealthy",
  "neo4j": "disconnected",
  "error": "Connection refused to bolt://localhost:7687"
}
```

### Behavior

1. Attempt to verify Neo4j connectivity
2. If successful, return 200 with healthy status
3. If failed, return 503 with error details
4. Response time should be < 1 second
5. Does not execute any Neo4j queries (just connectivity check)

### Error Handling

| Scenario | Status Code | Response |
|----------|-------------|----------|
| Neo4j down | 503 | Unhealthy status with error message |
| Neo4j timeout | 503 | Unhealthy status with timeout error |
| Driver error | 503 | Unhealthy status with error details |

### Performance

- **Expected Response Time:** < 500ms
- **Timeout:** 5 seconds
- **Caching:** No caching
- **Rate Limiting:** None

### Use Cases

1. **Load Balancer Health Checks**
   - Caddy uses this for upstream health monitoring
   - Remove unhealthy instances from rotation

2. **Monitoring Systems**
   - Prometheus/Grafana ping this endpoint
   - Alert on unhealthy status

3. **Deployment Verification**
   - CI/CD checks this after deployment
   - Ensure service is ready

### Examples

#### Healthy Service
```bash
curl http://localhost/api/health
```

Response:
```json
{
  "status": "healthy",
  "neo4j": "connected",
  "version": "1.0.0"
}
```

#### Unhealthy Service
```bash
curl http://localhost/api/health
```

Response (503):
```json
{
  "status": "unhealthy",
  "neo4j": "disconnected",
  "error": "ServiceUnavailable: Connection refused"
}
```

---

## GET /api/databases

### Purpose
List all Neo4j databases accessible to the API.

### Authentication
None required (public endpoint)

### Request

**HTTP Method:** GET

**URL:** `/api/databases`

**Headers:** None required

**Query Parameters:** None

**Request Body:** None

### Response

#### Success (200 OK)

```json
{
  "databases": [
    {
      "name": "neo4j",
      "default": true,
      "status": "online",
      "description": "Default database"
    },
    {
      "name": "system",
      "default": false,
      "status": "online",
      "description": "System database"
    },
    {
      "name": "investigation_001",
      "default": false,
      "status": "online",
      "description": "Investigation case 001"
    }
  ]
}
```

**Schema:**
```typescript
{
  databases: Array<{
    name: string           // Database name
    default: boolean       // Is this the default database?
    status?: string        // Optional: online, offline, etc.
    description?: string   // Optional: Human-readable description
  }>
}
```

#### Error (500 Internal Server Error)

**When:** Failed to query databases from Neo4j

```json
{
  "error": {
    "code": "DATABASE_QUERY_ERROR",
    "message": "Failed to list databases",
    "details": {
      "neo4j_error": "Permission denied"
    }
  }
}
```

### Behavior

1. Execute `SHOW DATABASES` against Neo4j
2. Parse results and format as JSON
3. Return list of all databases
4. Filter out inaccessible databases (future enhancement)
5. Cache results for 60 seconds (future enhancement)

### Error Handling

| Scenario | Status Code | Response |
|----------|-------------|----------|
| Neo4j query fails | 500 | Error with details |
| Permission denied | 500 | Error indicating lack of permissions |
| Neo4j disconnected | 503 | Service unavailable |

### Performance

- **Expected Response Time:** < 1 second
- **Timeout:** 10 seconds
- **Caching:** No caching in v1 (consider for v2)
- **Rate Limiting:** None

### Use Cases

1. **Database Selector UI**
   - Frontend dropdown to select target database
   - Show available databases to user

2. **Configuration Validation**
   - Verify database exists before sending queries
   - Check if database is online

3. **Documentation**
   - Auto-generate API docs with available databases
   - Help users understand available data sources

### Examples

#### List Databases
```bash
curl http://localhost/api/databases
```

Response:
```json
{
  "databases": [
    {
      "name": "neo4j",
      "default": true,
      "status": "online"
    },
    {
      "name": "investigation_fraud_2024",
      "default": false,
      "status": "online"
    },
    {
      "name": "investigation_cybercrime_001",
      "default": false,
      "status": "online"
    }
  ]
}
```

#### Error Case
```bash
curl http://localhost/api/databases
```

Response (500):
```json
{
  "error": {
    "code": "DATABASE_QUERY_ERROR",
    "message": "Failed to execute SHOW DATABASES",
    "details": {
      "neo4j_error": "Unauthorized"
    }
  }
}
```

---

## Implementation Notes

### Neo4j Driver Code

```python
# Health check
async def health_check():
    try:
        driver.verify_connectivity()
        return {"status": "healthy", "neo4j": "connected", "version": "1.0.0"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "neo4j": "disconnected", "error": str(e)}
        )

# List databases
async def list_databases():
    try:
        records, summary, keys = driver.execute_query(
            "SHOW DATABASES",
            routing_=RoutingControl.READ
        )
        databases = [
            {
                "name": record["name"],
                "default": record.get("default", False),
                "status": record.get("currentStatus", "unknown")
            }
            for record in records
        ]
        return {"databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Testing Requirements

**Test Cases for /api/health:**
1. ✅ Neo4j connected → 200 healthy
2. ✅ Neo4j disconnected → 503 unhealthy
3. ✅ Neo4j timeout → 503 unhealthy
4. ✅ Response time < 1 second

**Test Cases for /api/databases:**
1. ✅ List databases → 200 with array
2. ✅ No databases → 200 with empty array
3. ✅ Neo4j error → 500 with error
4. ✅ Default database marked correctly
5. ✅ Response format matches schema

### Future Enhancements

1. **Detailed Health Info**
   ```json
   {
     "status": "healthy",
     "neo4j": {
       "connected": true,
       "version": "5.14.0",
       "edition": "enterprise",
       "cluster_members": 3
     },
     "api": {
       "version": "1.0.0",
       "uptime_seconds": 3600
     }
   }
   ```

2. **Database Metadata**
   ```json
   {
     "name": "investigation_001",
     "size_bytes": 1048576,
     "node_count": 10000,
     "relationship_count": 50000,
     "last_accessed": "2025-11-03T12:00:00Z"
   }
   ```

3. **Filtered Database List**
   - Only show databases user has access to
   - Based on permissions/authentication
