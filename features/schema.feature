Feature: Schema Discovery
  As an API user
  I want to discover the database schema
  So that I can understand available node labels and relationship types

  Background:
    Given the API is running
    And the Neo4j database "neo4j" is connected
    And I have a valid API key

  @schema @labels @smoke
  Scenario: Get all node labels from database
    Given the database contains nodes with labels:
      | label    |
      | Person   |
      | Company  |
      | Product  |
      | Order    |
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the response status code should be 200
    And the JSON response should have a "types" array
    And the types array should contain "Person"
    And the types array should contain "Company"
    And the types array should contain "Product"
    And the types array should contain "Order"
    And the types array should have 4 items

  @schema @labels
  Scenario: Get node labels from empty database
    Given the database contains no nodes
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the response status code should be 200
    And the types array should be empty

  @schema @relationships @smoke
  Scenario: Get all relationship types from database
    Given the database contains relationships with types:
      | type      |
      | WORKS_FOR |
      | MANAGES   |
      | KNOWS     |
      | PURCHASED |
    When I send a GET request to "/api/neo4j/graph/schema/edge/types" with authentication
    Then the response status code should be 200
    And the JSON response should have a "types" array
    And the types array should contain "WORKS_FOR"
    And the types array should contain "MANAGES"
    And the types array should contain "KNOWS"
    And the types array should contain "PURCHASED"
    And the types array should have 4 items

  @schema @relationships
  Scenario: Get relationship types from database without relationships
    Given the database contains nodes but no relationships
    When I send a GET request to "/api/neo4j/graph/schema/edge/types" with authentication
    Then the response status code should be 200
    And the types array should be empty

  @schema @properties @smoke
  Scenario: Get properties for a specific node label
    Given the database contains Person nodes with properties:
      | property | type   |
      | name     | string |
      | age      | number |
      | email    | string |
      | active   | boolean|
    When I send a GET request to "/api/neo4j/graph/schema/node/types/Person/properties" with authentication
    Then the response status code should be 200
    And the JSON response should have a "properties" array
    And the properties array should contain "name"
    And the properties array should contain "age"
    And the properties array should contain "email"
    And the properties array should contain "active"

  @schema @properties
  Scenario: Get properties for a specific relationship type
    Given the database contains WORKS_FOR relationships with properties:
      | property | type   |
      | since    | date   |
      | role     | string |
      | salary   | number |
    When I send a GET request to "/api/neo4j/graph/schema/edge/types/WORKS_FOR/properties" with authentication
    Then the response status code should be 200
    And the properties array should contain "since"
    And the properties array should contain "role"
    And the properties array should contain "salary"

  @schema @auth
  Scenario Outline: Schema endpoints require authentication
    When I send a GET request to "<endpoint>" without authentication
    Then the response status code should be 403
    And the error code should be "MISSING_API_KEY"

    Examples:
      | endpoint                                |
      | /api/neo4j/graph/schema/node/types      |
      | /api/neo4j/graph/schema/edge/types      |

  @schema @database
  Scenario: Schema endpoints fail when database does not exist
    When I send a GET request to "/api/nonexistent_db/graph/schema/node/types" with authentication
    Then the response status code should be 404
    And the error code should be "DATABASE_NOT_FOUND"

  @schema @error
  Scenario: Schema query fails due to database error
    Given the Neo4j database will return an error for schema queries
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the response status code should be 500
    And the error code should be "QUERY_EXECUTION_ERROR"
    And the error message should contain "Failed to retrieve node labels"

  @schema @format
  Scenario: Schema response format is correct
    Given the database contains node labels
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the response status code should be 200
    And the response should match schema:
      """
      {
        "types": ["string", "array"]
      }
      """

  @schema @sorting
  Scenario: Node labels are returned in alphabetical order
    Given the database contains nodes with labels "Zebra", "Apple", "Mango", "Banana"
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the response status code should be 200
    And the types array should be sorted alphabetically

  @schema @integration
  Scenario: Schema endpoints work across different databases
    Given the Neo4j databases "neo4j" and "investigation_001" exist
    And database "neo4j" has node labels "Person", "Company"
    And database "investigation_001" has node labels "Suspect", "Evidence"
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the types array should contain "Person"
    And the types array should contain "Company"
    When I send a GET request to "/api/investigation_001/graph/schema/node/types" with authentication
    Then the types array should contain "Suspect"
    And the types array should contain "Evidence"
    And the types array should not contain "Person"

  @schema @performance
  Scenario: Schema retrieval completes quickly
    Given the database contains 50 different node labels
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the response time should be less than 1000 milliseconds
    And the response status code should be 200
    And the types array should have 50 items

  @schema @caching
  Scenario: Schema results can be cached
    When I send a GET request to "/api/neo4j/graph/schema/node/types" with authentication
    Then the response should include caching headers
    And the cache duration should be appropriate for schema data

  @schema @comprehensive
  Scenario: Retrieve complete schema information
    Given the database has a complex schema with:
      | node_labels      | relationship_types |
      | Person           | WORKS_FOR          |
      | Company          | MANAGES            |
      | Product          | PURCHASED          |
      | Order            | CONTAINS           |
    When I retrieve all node types
    And I retrieve all relationship types
    Then I should have complete schema information
    And the schema should include 4 node labels
    And the schema should include 4 relationship types
