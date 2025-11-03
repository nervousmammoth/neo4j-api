Feature: API Key Authentication
  As an API administrator
  I want to secure API endpoints with API key authentication
  So that only authorized users can access protected resources

  Background:
    Given the API is running
    And the configured API key is "test-api-key-12345"

  @auth @security @smoke
  Scenario: Valid API key allows access to protected endpoint
    Given the Neo4j database is connected
    When I send a GET request to "/api/neo4j/graph/nodes/count" with headers:
      | header     | value               |
      | X-API-Key  | test-api-key-12345  |
    Then the response status code should be 200

  @auth @security @critical
  Scenario: Missing API key is rejected with 403
    Given the Neo4j database is connected
    When I send a GET request to "/api/neo4j/graph/nodes/count" without authentication
    Then the response status code should be 403
    And the JSON response should have an "error" object
    And the error code should be "MISSING_API_KEY"
    And the error message should contain "API key is required"
    And the error details should include:
      | field  | value     |
      | header | X-API-Key |

  @auth @security @critical
  Scenario: Invalid API key is rejected with 403
    Given the Neo4j database is connected
    When I send a GET request to "/api/neo4j/graph/nodes/count" with headers:
      | header     | value          |
      | X-API-Key  | wrong-api-key  |
    Then the response status code should be 403
    And the JSON response should have an "error" object
    And the error code should be "INVALID_API_KEY"
    And the error message should contain "Invalid API key"

  @auth @security
  Scenario: Empty API key is rejected with 403
    Given the Neo4j database is connected
    When I send a GET request to "/api/neo4j/graph/nodes/count" with headers:
      | header     | value |
      | X-API-Key  |       |
    Then the response status code should be 403
    And the error code should be "MISSING_API_KEY"

  @auth @security
  Scenario: API key validation is case-sensitive
    Given the Neo4j database is connected
    When I send a GET request to "/api/neo4j/graph/nodes/count" with headers:
      | header     | value               |
      | X-API-Key  | TEST-API-KEY-12345  |
    Then the response status code should be 403
    And the error code should be "INVALID_API_KEY"

  @auth @public @smoke
  Scenario: Public health endpoint does not require authentication
    Given the Neo4j database is connected
    When I send a GET request to "/api/health" without authentication
    Then the response status code should be 200
    And the JSON response should have field "status" with value "healthy"

  @auth @public
  Scenario Outline: Public endpoints are accessible without API key
    Given the Neo4j database is connected
    When I send a GET request to "<endpoint>" without authentication
    Then the response status code should not be 403

    Examples:
      | endpoint           |
      | /api/health        |
      | /api/databases     |
      | /api/docs          |
      | /api/redoc         |
      | /api/openapi.json  |

  @auth @protected @integration
  Scenario Outline: Protected endpoints require valid API key
    Given the Neo4j database is connected
    When I send a GET request to "<endpoint>" without authentication
    Then the response status code should be 403
    And the error code should be "MISSING_API_KEY"

    Examples:
      | endpoint                        |
      | /api/neo4j/search/nodes         |
      | /api/neo4j/search/edges         |
      | /api/neo4j/graph/query          |
      | /api/neo4j/graph/nodes/123      |
      | /api/neo4j/graph/schema/labels  |

  @auth @protected @integration
  Scenario: Valid API key grants access to all protected endpoints
    Given the Neo4j database is connected
    And I have a valid API key "test-api-key-12345"
    When I send authenticated requests to the following endpoints:
      | method | endpoint                       |
      | GET    | /api/neo4j/search/nodes        |
      | GET    | /api/neo4j/graph/nodes/count   |
      | GET    | /api/neo4j/graph/schema/labels |
    Then all requests should return status code 200 or 400
    And none of the requests should return status code 403

  @auth @security
  Scenario: API key header name is case-insensitive
    Given the Neo4j database is connected
    When I send a GET request to "/api/neo4j/graph/nodes/count" with headers:
      | header     | value               |
      | x-api-key  | test-api-key-12345  |
    Then the response status code should be 200

  @auth @validation
  Scenario: API key with whitespace is treated as invalid
    Given the Neo4j database is connected
    When I send a GET request to "/api/neo4j/graph/nodes/count" with headers:
      | header     | value                    |
      | X-API-Key  |  test-api-key-12345      |
    Then the response status code should be 403
    And the error code should be "INVALID_API_KEY"

  @auth @security @logging
  Scenario: Failed authentication attempts are logged
    Given the Neo4j database is connected
    And the application logging is enabled
    When I send a GET request to "/api/neo4j/graph/nodes/count" with headers:
      | header     | value                 |
      | X-API-Key  | unauthorized-attempt  |
    Then the response status code should be 403
    And a failed authentication attempt should be logged with details:
      | field      | value                      |
      | event      | authentication_failed       |
      | api_key    | unauthorized-attempt        |
      | endpoint   | /api/neo4j/graph/nodes/count|

  @auth @database
  Scenario: Authentication works across different databases
    Given the Neo4j databases "neo4j" and "investigation_001" exist
    When I send a GET request to "/api/neo4j/graph/nodes/count" with valid API key
    Then the response status code should be 200
    When I send a GET request to "/api/investigation_001/graph/nodes/count" with valid API key
    Then the response status code should be 200
    When I send a GET request to "/api/investigation_001/graph/nodes/count" without authentication
    Then the response status code should be 403
