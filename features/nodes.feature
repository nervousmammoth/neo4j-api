Feature: Node Operations
  As an API user
  I want to retrieve nodes and their relationships
  So that I can explore the graph structure and node neighborhoods

  Background:
    Given the API is running
    And the Neo4j database "neo4j" is connected
    And I have a valid API key

  @nodes @get @smoke
  Scenario: Get node by ID with adjacent edges
    Given the database contains a node with ID "123":
      | field  | value             |
      | labels | Person            |
      | name   | Alice Smith       |
      | age    | 30                |
    And node "123" has an outgoing WORKS_FOR relationship to node "456"
    When I send a GET request to "/api/neo4j/graph/nodes/123" with authentication
    Then the response status code should be 200
    And the nodes array should contain 1 item
    And the first node should have ID "123"
    And the first node categories should include "Person"
    And the first node properties should have "name" with value "Alice Smith"
    And the edges array should contain 1 item
    And the first edge should have source "123" and target "456"

  @nodes @get @error
  Scenario: Get non-existent node returns 404
    When I send a GET request to "/api/neo4j/graph/nodes/99999" with authentication
    Then the response status code should be 404
    And the error code should be "NODE_NOT_FOUND"
    And the error message should contain "Node with ID '99999' not found"
    And the error details should have field "node_id" with value "99999"
    And the error details should have field "database" with value "neo4j"

  @nodes @get @validation
  Scenario: Invalid node ID format returns 400
    When I send a GET request to "/api/neo4j/graph/nodes/invalid-id" with authentication
    Then the response status code should be 400
    And the error code should be "INVALID_NODE_ID"
    And the error message should contain "Node ID must be a valid integer"

  @nodes @get @statistics
  Scenario: Get node with degree statistics
    Given the database contains a node with ID "123" that has 5 relationships
    When I send a GET request to "/api/neo4j/graph/nodes/123?withDegree=true" with authentication
    Then the response status code should be 200
    And the first node data should have field "statistics"
    And the statistics should have field "degree" with value 5

  @nodes @get @statistics
  Scenario: Get node with digest statistics
    Given the database contains a node with ID "123"
    When I send a GET request to "/api/neo4j/graph/nodes/123?withDigest=true" with authentication
    Then the response status code should be 200
    And the first node data should have field "statistics"

  @nodes @count @smoke
  Scenario: Get total node count in database
    Given the database contains 150 nodes
    When I send a GET request to "/api/neo4j/graph/nodes/count" with authentication
    Then the response status code should be 200
    And the JSON response should have field "count" with value 150

  @nodes @count
  Scenario: Get node count for empty database
    Given the database is empty
    When I send a GET request to "/api/neo4j/graph/nodes/count" with authentication
    Then the response status code should be 200
    And the JSON response should have field "count" with value 0

  @nodes @expand @smoke
  Scenario: Expand node neighborhood
    Given the database contains a node with ID "123"
    And node "123" is connected to nodes "456", "789", and "101"
    When I send a POST request to "/api/neo4j/graph/nodes/expand" with authentication and body:
      """
      {
        "nodeIds": ["123"],
        "depth": 1
      }
      """
    Then the response status code should be 200
    And the nodes array should contain at least 4 items
    And the edges array should contain at least 3 items

  @nodes @expand
  Scenario: Expand with maximum depth limit
    Given the database contains a connected graph
    When I send a POST request to "/api/neo4j/graph/nodes/expand" with authentication and body:
      """
      {
        "nodeIds": ["123"],
        "depth": 2,
        "maxNodes": 100
      }
      """
    Then the response status code should be 200
    And the nodes array should not exceed 100 items

  @nodes @expand @validation
  Scenario: Expand requires nodeIds parameter
    When I send a POST request to "/api/neo4j/graph/nodes/expand" with authentication and body:
      """
      {
        "depth": 1
      }
      """
    Then the response status code should be 422
    And the error code should be "VALIDATION_ERROR"
    And the validation errors should include field "nodeIds"

  @nodes @auth
  Scenario Outline: Node endpoints require authentication
    When I send a GET request to "<endpoint>" without authentication
    Then the response status code should be 403
    And the error code should be "MISSING_API_KEY"

    Examples:
      | endpoint                        |
      | /api/neo4j/graph/nodes/123      |
      | /api/neo4j/graph/nodes/count    |

  @nodes @database
  Scenario: Node operations fail when database does not exist
    When I send a GET request to "/api/nonexistent_db/graph/nodes/123" with authentication
    Then the response status code should be 404
    And the error code should be "DATABASE_NOT_FOUND"

  @nodes @format @linkurious
  Scenario: Node response format is Linkurious-compatible
    Given the database contains a node with ID "123" and labels "Person", "Employee"
    When I send a GET request to "/api/neo4j/graph/nodes/123" with authentication
    Then the response status code should be 200
    And each node should have structure:
      | field | type   |
      | id    | string |
      | data  | object |
    And each node data should have:
      | field      | type  |
      | categories | array |
      | properties | object|

  @nodes @get @edges
  Scenario: Retrieved node includes all adjacent edges
    Given the database contains a node with ID "123"
    And node "123" has 3 incoming edges and 2 outgoing edges
    When I send a GET request to "/api/neo4j/graph/nodes/123" with authentication
    Then the response status code should be 200
    And the edges array should contain 5 items
    And the edges should include both incoming and outgoing relationships

  @nodes @expand @direction
  Scenario: Expand node in specific direction
    Given the database contains a node with ID "123"
    When I send a POST request to "/api/neo4j/graph/nodes/expand" with authentication and body:
      """
      {
        "nodeIds": ["123"],
        "depth": 1,
        "direction": "outgoing"
      }
      """
    Then the response status code should be 200
    And the edges should only include outgoing relationships from node "123"

  @nodes @performance
  Scenario: Node retrieval completes quickly
    Given the database contains a node with ID "123"
    When I send a GET request to "/api/neo4j/graph/nodes/123" with authentication
    Then the response time should be less than 1000 milliseconds
    And the response status code should be 200
