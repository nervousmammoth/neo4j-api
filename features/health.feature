Feature: Health & Metadata Endpoints
  As an API consumer
  I want to check the health status and discover available databases
  So that I can monitor the service and select the appropriate database for my operations

  Background:
    Given the API is running

  @health @public @smoke
  Scenario: Check API health when Neo4j is connected
    Given the Neo4j database is connected and responsive
    When I send a GET request to "/api/health"
    Then the response status code should be 200
    And the response time should be less than 500 milliseconds
    And the JSON response should contain:
      | field   | value     |
      | status  | healthy   |
      | neo4j   | connected |
      | version | 1.0.0     |

  @health @error
  Scenario: Check API health when Neo4j is disconnected
    Given the Neo4j database is disconnected
    When I send a GET request to "/api/health"
    Then the response status code should be 503
    And the JSON response should contain:
      | field  | value        |
      | status | unhealthy    |
      | neo4j  | disconnected |
    And the response should contain an "error" field

  @health @error
  Scenario: Check API health when Neo4j connection times out
    Given the Neo4j database connection will timeout
    When I send a GET request to "/api/health"
    Then the response status code should be 503
    And the JSON response should have field "status" with value "unhealthy"
    And the response should contain an "error" field
    And the error message should mention "timeout"

  @databases @public @smoke
  Scenario: List all available databases
    Given the Neo4j database is connected
    And the following databases exist:
      | name                          | default | status | description              |
      | neo4j                         | true    | online | Default database         |
      | system                        | false   | online | System database          |
      | investigation_001             | false   | online | Investigation case 001   |
      | investigation_fraud_2024      | false   | online | Fraud investigation 2024 |
    When I send a GET request to "/api/databases"
    Then the response status code should be 200
    And the JSON response should have a "databases" array
    And the "databases" array should contain 4 items
    And the database "neo4j" should be marked as default
    And all databases should have required fields:
      | field  |
      | name   |
      | default|
      | status |

  @databases @public
  Scenario: List databases when only default database exists
    Given the Neo4j database is connected
    And only the default database "neo4j" exists
    When I send a GET request to "/api/databases"
    Then the response status code should be 200
    And the JSON response should have a "databases" array
    And the "databases" array should contain 1 item
    And the database "neo4j" should be marked as default

  @databases @error
  Scenario: List databases when Neo4j query fails
    Given the Neo4j database is connected
    But the "SHOW DATABASES" query will fail with error "Permission denied"
    When I send a GET request to "/api/databases"
    Then the response status code should be 500
    And the JSON response should have an "error" object
    And the error code should be "DATABASE_QUERY_ERROR"
    And the error message should contain "Failed to list databases"

  @databases @error
  Scenario: List databases when Neo4j is disconnected
    Given the Neo4j database is disconnected
    When I send a GET request to "/api/databases"
    Then the response status code should be 503
    And the JSON response should have an "error" object
    And the error should indicate service unavailability

  @health @performance
  Scenario: Health check responds quickly
    Given the Neo4j database is connected
    When I send a GET request to "/api/health"
    Then the response time should be less than 1000 milliseconds
    And the response status code should be 200

  @databases @validation
  Scenario: Database list includes correct metadata
    Given the Neo4j database is connected
    And the database "investigation_cybercrime_001" exists with:
      | field       | value                       |
      | name        | investigation_cybercrime_001|
      | default     | false                       |
      | status      | online                      |
      | description | Cybercrime investigation    |
    When I send a GET request to "/api/databases"
    Then the response status code should be 200
    And the "databases" array should include database "investigation_cybercrime_001"
    And the database "investigation_cybercrime_001" should have:
      | field       | value                       |
      | name        | investigation_cybercrime_001|
      | default     | false                       |
      | status      | online                      |
