Feature: Cypher Query Execution
  As an API user
  I want to execute Cypher queries against Neo4j databases
  So that I can retrieve graph data with custom query logic

  Background:
    Given the API is running
    And the Neo4j database "neo4j" is connected
    And I have a valid API key

  @query @smoke
  Scenario: Execute simple MATCH query successfully
    Given the database contains nodes and relationships:
      | node_id | labels  | name       |
      | 123     | Person  | Alice      |
      | 456     | Company | Acme Corp  |
    And a relationship WORKS_FOR from node 123 to node 456
    When I execute the Cypher query:
      """
      MATCH (p:Person)-[r:WORKS_FOR]->(c:Company)
      RETURN p, r, c
      """
    Then the response status code should be 200
    And the response should have field "nodes" as an array
    And the response should have field "edges" as an array
    And the nodes array should contain 2 items
    And the edges array should contain 1 item

  @query @parameters
  Scenario: Execute query with parameters
    Given the database contains person nodes with ages
    When I execute the Cypher query with parameters:
      """
      MATCH (p:Person)
      WHERE p.age > $min_age
      RETURN p
      LIMIT $limit
      """
      | parameter | value |
      | min_age   | 25    |
      | limit     | 10    |
    Then the response status code should be 200
    And the query should execute with correct parameters

  @query @security @critical
  Scenario Outline: Block write operations (CREATE, DELETE, MERGE, SET, REMOVE)
    When I execute the Cypher query:
      """
      <query>
      """
    Then the response status code should be 403
    And the error code should be "WRITE_OPERATION_FORBIDDEN"
    And the error message should contain "Write operations are not allowed"
    And the error details should include field "forbidden_keyword" with value "<keyword>"
    And the error details should list allowed operations

    Examples:
      | keyword | query                                          |
      | CREATE  | CREATE (n:Person {name: 'Bob'}) RETURN n       |
      | DELETE  | MATCH (n) DELETE n                             |
      | MERGE   | MERGE (n:Person {email: 'test@example.com'})   |
      | SET     | MATCH (n:Person) SET n.age = 30                |
      | REMOVE  | MATCH (n:Person) REMOVE n.email                |
      | DROP    | DROP INDEX person_name_index                   |

  @query @allowed
  Scenario Outline: Allow read-only operations
    When I execute the Cypher query:
      """
      <query>
      """
    Then the response status code should not be 403

    Examples:
      | query                                      |
      | MATCH (n) RETURN n LIMIT 10                |
      | MATCH (n)-[r]->(m) RETURN n, r, m          |
      | CALL db.labels()                           |
      | SHOW DATABASES                             |
      | MATCH (n) WITH n.name AS name RETURN name  |
      | OPTIONAL MATCH (n:Person) RETURN n         |
      | UNWIND [1,2,3] AS x RETURN x               |

  @query @error
  Scenario: Return error for invalid Cypher syntax
    When I execute the Cypher query:
      """
      MATCH (n R n
      """
    Then the response status code should be 400
    And the error code should be "QUERY_SYNTAX_ERROR"
    And the error message should contain "Invalid Cypher query syntax"
    And the error details should have field "query"
    And the error details should have field "neo4j_error"

  @query @timeout
  Scenario: Timeout for long-running queries
    When I execute a query that will take longer than 60 seconds
    Then the response status code should be 504
    And the error code should be "QUERY_TIMEOUT"
    And the error message should contain "exceeded timeout limit"
    And the error details should have field "timeout_seconds" with value 60

  @query @format @linkurious
  Scenario: Response format is Linkurious-compatible
    Given the database contains a graph:
      | node_id | labels  | name      |
      | 123     | Person  | Alice     |
      | 456     | Company | Acme Corp |
    And a WORKS_FOR relationship from 123 to 456 with property role "Engineer"
    When I execute the Cypher query:
      """
      MATCH (p:Person)-[r:WORKS_FOR]->(c:Company)
      RETURN p, r, c
      """
    Then the response should have nodes with structure:
      | field | type   |
      | id    | string |
      | data  | object |
    And each node data should have:
      | field      | type  |
      | categories | array |
      | properties | object|
    And the response should have edges with structure:
      | field  | type   |
      | id     | string |
      | source | string |
      | target | string |
      | data   | object |
    And each edge data should have:
      | field      | type   |
      | type       | string |
      | properties | object |

  @query @meta
  Scenario: Response includes metadata
    When I execute the Cypher query:
      """
      MATCH (n:Person) RETURN n LIMIT 5
      """
    Then the response status code should be 200
    And the response should have field "meta" as an object
    And the meta should have field "query_type" with value "r"
    And the meta should have field "records_returned"
    And the meta should have field "execution_time_ms"

  @query @empty
  Scenario: Query returns empty result set
    Given the database is empty
    When I execute the Cypher query:
      """
      MATCH (n:NonexistentLabel) RETURN n
      """
    Then the response status code should be 200
    And the nodes array should be empty
    And the edges array should be empty
    And the meta should have field "records_returned" with value 0

  @query @database
  Scenario: Query fails when database does not exist
    When I send a POST request to "/api/nonexistent_db/graph/query" with authentication and body:
      """
      {"query": "MATCH (n) RETURN n"}
      """
    Then the response status code should be 404
    And the error code should be "DATABASE_NOT_FOUND"

  @query @auth
  Scenario: Query endpoint requires authentication
    When I send a POST request to "/api/neo4j/graph/query" without authentication and body:
      """
      {"query": "MATCH (n) RETURN n"}
      """
    Then the response status code should be 403
    And the error code should be "MISSING_API_KEY"

  @query @validation
  Scenario: Query field is required in request body
    When I send a POST request to "/api/neo4j/graph/query" with authentication and body:
      """
      {"parameters": {"age": 25}}
      """
    Then the response status code should be 422
    And the error code should be "VALIDATION_ERROR"
    And the validation errors should include field "query"

  @query @deduplication
  Scenario: Duplicate nodes are deduplicated in results
    Given the database contains nodes with IDs 123 and 456
    When I execute the Cypher query:
      """
      MATCH (n)
      WHERE id(n) IN [123, 456]
      RETURN n, n AS duplicate
      """
    Then the response status code should be 200
    And the nodes array should contain exactly 2 unique nodes
    And node 123 should appear only once in the results
    And node 456 should appear only once in the results

  @query @routing
  Scenario: Queries are routed to read replicas
    When I execute a read query
    Then the query should use READ routing control
    And the query should be executed on a read replica if available

  @query @limit
  Scenario: Truncation flag indicates LIMIT was applied
    Given the database contains 100 person nodes
    When I execute the Cypher query:
      """
      MATCH (n:Person) RETURN n LIMIT 10
      """
    Then the response status code should be 200
    And the response should have field "truncatedByLimit" with value true
    And the nodes array should contain 10 items

  @query @complex
  Scenario: Execute complex query with multiple clauses
    When I execute the Cypher query:
      """
      MATCH (p:Person)
      WHERE p.age > 25
      WITH p
      ORDER BY p.name
      SKIP 5
      LIMIT 10
      OPTIONAL MATCH (p)-[r:WORKS_FOR]->(c:Company)
      RETURN p, r, c
      """
    Then the response status code should be 200
    And the query should execute successfully
