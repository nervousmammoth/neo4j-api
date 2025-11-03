Feature: Search Endpoints
  As an API user
  I want to search for nodes and edges in the graph database
  So that I can find relevant data using full-text search with fuzzy matching

  Background:
    Given the API is running
    And the Neo4j database "neo4j" is connected
    And I have a valid API key

  # Node Search Tests

  @search @nodes @smoke
  Scenario: Search nodes by property value
    Given the database contains nodes:
      | id  | labels   | name          | age |
      | 123 | Person   | Alice Smith   | 30  |
      | 456 | Person   | Alice Johnson | 28  |
      | 789 | Person   | Bob Williams  | 35  |
    When I search for nodes with query "Alice"
    Then the response status code should be 200
    And the JSON response should have field "type" with value "node"
    And the response should contain 2 results
    And the results should include node "123" with name "Alice Smith"
    And the results should include node "456" with name "Alice Johnson"

  @search @nodes
  Scenario: Search with fuzzy matching for typos
    Given the database contains nodes:
      | id  | labels | name    |
      | 123 | Person | Alice   |
      | 456 | Person | Alicia  |
    When I search for nodes with query "Alise" and fuzziness 0.8
    Then the response status code should be 200
    And the response should contain at least 1 result
    And the results should include matches for "Alice"

  @search @nodes @empty
  Scenario: Search returns empty results when no matches found
    Given the database contains nodes:
      | id  | labels | name |
      | 123 | Person | Bob  |
    When I search for nodes with query "NonexistentPerson"
    Then the response status code should be 200
    And the JSON response should have field "type" with value "node"
    And the JSON response should have field "totalHits" with value 0
    And the results array should be empty
    And the JSON response should have field "moreResults" with value false

  @search @nodes @pagination
  Scenario: Search with pagination parameters
    Given the database contains 50 person nodes
    When I search for nodes with query "Person" and parameters:
      | parameter | value |
      | size      | 10    |
      | from      | 20    |
    Then the response status code should be 200
    And the response should contain 10 results
    And the JSON response should have field "moreResults" with value true

  @search @nodes @case-insensitive
  Scenario Outline: Search is case-insensitive
    Given the database contains a node with name "<stored_name>"
    When I search for nodes with query "<search_query>"
    Then the response status code should be 200
    And the response should contain at least 1 result
    And the first result should have property "name" with value "<stored_name>"

    Examples:
      | stored_name | search_query |
      | Alice       | alice        |
      | alice       | ALICE        |
      | Alice       | ALiCe        |

  @search @nodes @validation
  Scenario: Search fails when query parameter is missing
    When I send a GET request to "/api/neo4j/search/node/full" with authentication
    Then the response status code should be 422
    And the JSON response should have an "error" object
    And the error code should be "VALIDATION_ERROR"
    And the error message should contain "validation failed"
    And the validation errors should include field "q"

  @search @nodes @validation
  Scenario Outline: Search validates parameter ranges
    When I search for nodes with query "test" and parameters:
      | parameter | value    |
      | <param>   | <value>  |
    Then the response status code should be <status>
    And the error should indicate invalid parameter "<param>"

    Examples:
      | param     | value | status |
      | fuzziness | 1.5   | 422    |
      | fuzziness | -0.1  | 422    |
      | size      | 0     | 422    |
      | size      | 1001  | 422    |
      | from      | -1    | 422    |

  @search @nodes @database
  Scenario: Search fails when database does not exist
    When I send a GET request to "/api/nonexistent_db/search/node/full?q=test" with authentication
    Then the response status code should be 404
    And the JSON response should have an "error" object
    And the error code should be "DATABASE_NOT_FOUND"
    And the error message should contain "Database 'nonexistent_db' not found"
    And the error details should have field "database" with value "nonexistent_db"

  @search @nodes @auth
  Scenario: Node search requires authentication
    When I send a GET request to "/api/neo4j/search/node/full?q=test" without authentication
    Then the response status code should be 403
    And the error code should be "MISSING_API_KEY"

  @search @nodes @performance
  Scenario: Search completes within performance threshold
    Given the database contains 1000 nodes
    When I search for nodes with query "test"
    Then the response time should be less than 2000 milliseconds
    And the response status code should be 200

  @search @nodes @properties
  Scenario: Search matches across multiple properties
    Given the database contains a node with properties:
      | property | value              |
      | name     | John Doe           |
      | email    | john@example.com   |
      | company  | Acme Corporation   |
    When I search for nodes with query "Acme"
    Then the response status code should be 200
    And the response should contain at least 1 result
    And the result should have property "company" with value "Acme Corporation"

  # Edge Search Tests

  @search @edges @smoke
  Scenario: Search edges by property value
    Given the database contains relationships:
      | id  | type      | source | target | role     | since      |
      | 789 | WORKS_FOR | 123    | 456    | Engineer | 2020-01-15 |
      | 790 | WORKS_FOR | 124    | 456    | Manager  | 2019-06-01 |
    When I search for edges with query "Engineer"
    Then the response status code should be 200
    And the JSON response should have field "type" with value "edge"
    And the response should contain 1 result
    And the first result should have:
      | field  | value     |
      | id     | 789       |
      | type   | WORKS_FOR |
      | source | 123       |
      | target | 456       |

  @search @edges @empty
  Scenario: Edge search returns empty results when no matches
    Given the database contains relationships without matching properties
    When I search for edges with query "NonexistentProperty"
    Then the response status code should be 200
    And the JSON response should have field "type" with value "edge"
    And the JSON response should have field "totalHits" with value 0
    And the results array should be empty

  @search @edges @auth
  Scenario: Edge search requires authentication
    When I send a GET request to "/api/neo4j/search/edge/full?q=test" without authentication
    Then the response status code should be 403
    And the error code should be "MISSING_API_KEY"

  @search @edges @database
  Scenario: Edge search fails when database does not exist
    When I send a GET request to "/api/invalid_db/search/edge/full?q=test" with authentication
    Then the response status code should be 404
    And the error code should be "DATABASE_NOT_FOUND"

  # Multi-database Tests

  @search @database @integration
  Scenario: Search works across different databases
    Given the Neo4j databases "neo4j" and "investigation_001" exist
    And database "neo4j" contains a node with name "Alice"
    And database "investigation_001" contains a node with name "Bob"
    When I search for nodes with query "Alice" in database "neo4j"
    Then the response should contain 1 result
    And the result should have property "name" with value "Alice"
    When I search for nodes with query "Bob" in database "investigation_001"
    Then the response should contain 1 result
    And the result should have property "name" with value "Bob"

  # Result Format Tests

  @search @format
  Scenario: Node search results include all required fields
    Given the database contains a node with:
      | field      | value                    |
      | id         | 123                      |
      | labels     | Person,Employee          |
      | name       | Alice                    |
      | age        | 30                       |
    When I search for nodes with query "Alice"
    Then the response status code should be 200
    And the first result should have field "id"
    And the first result should have field "labels" as an array
    And the first result should have field "properties" as an object
    And the result labels should include "Person"
    And the result labels should include "Employee"
    And the result properties should have field "name" with value "Alice"
    And the result properties should have field "age" with value 30

  @search @format
  Scenario: Edge search results include source and target node IDs
    Given the database contains a relationship:
      | id     | type      | source | target |
      | 789    | KNOWS     | 123    | 456    |
    When I search for edges with query "KNOWS"
    Then the response status code should be 200
    And the first result should have field "id" with value "789"
    And the first result should have field "type" with value "KNOWS"
    And the first result should have field "source" with value "123"
    And the first result should have field "target" with value "456"
