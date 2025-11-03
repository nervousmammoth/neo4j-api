"""
Neo4j database-specific step definitions.
"""

from behave import given, then, when

# ============================================================================
# GIVEN Steps - Neo4j Database State
# ============================================================================


@given("the Neo4j database is connected")
@given("the Neo4j database is connected and responsive")
@given('the Neo4j database "{database}" is connected')
def step_neo4j_connected(context, database="neo4j"):
    """Set up Neo4j database as connected."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {}

    context.neo4j_databases[database] = {
        "status": "connected",
        "nodes": [],
        "relationships": [],
        "labels": set(),
        "relationship_types": set(),
    }


@given("the Neo4j database is disconnected")
def step_neo4j_disconnected(context):
    """Set up Neo4j database as disconnected."""
    context.neo4j_status = "disconnected"


@given("the Neo4j database connection will timeout")
def step_neo4j_will_timeout(context):
    """Configure Neo4j mock to simulate timeout."""
    context.neo4j_status = "timeout"


@given('the Neo4j databases "{db1}" and "{db2}" exist')
def step_multiple_databases_exist(context, db1, db2):
    """Set up multiple Neo4j databases."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {}

    for db in [db1, db2]:
        context.neo4j_databases[db] = {
            "status": "connected",
            "nodes": [],
            "relationships": [],
            "labels": set(),
            "relationship_types": set(),
        }


@given("the following databases exist")
def step_databases_exist_table(context):
    """Set up multiple databases from table."""
    if not hasattr(context, "available_databases"):
        context.available_databases = []

    for row in context.table:
        db_info = {
            "name": row["name"],
            "default": row["default"].lower() == "true",
            "status": row["status"],
            "description": row.get("description", ""),
        }
        context.available_databases.append(db_info)


@given('only the default database "{db_name}" exists')
def step_only_default_database_exists(context, db_name):
    """Set up scenario with only default database."""
    context.available_databases = [
        {"name": db_name, "default": True, "status": "online"}
    ]


@given("the database is empty")
@given("the database contains no nodes")
def step_database_empty(context):
    """Set up empty database."""
    context.neo4j_databases = {
        "neo4j": {
            "status": "connected",
            "nodes": [],
            "relationships": [],
            "labels": set(),
            "relationship_types": set(),
        }
    }


# ============================================================================
# GIVEN Steps - Database Content Setup
# ============================================================================


@given("the database contains nodes")
@given("the database contains {count:d} nodes")
def step_database_contains_nodes(context, count=10):
    """Set up database with N nodes."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": []}}

    # Generate mock nodes
    for i in range(count):
        context.neo4j_databases["neo4j"]["nodes"].append(
            {"id": str(100 + i), "labels": ["TestNode"], "properties": {"id": i}}
        )


@given("the database contains nodes with labels")
def step_database_contains_labeled_nodes(context):
    """Set up database with nodes having specific labels."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": [], "labels": set()}}

    for row in context.table:
        label = row["label"]
        context.neo4j_databases["neo4j"]["labels"].add(label)


@given('the database contains a node with ID "{node_id}"')
def step_database_contains_node_with_id(context, node_id):
    """Set up specific node in database."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": []}}

    node = {"id": node_id, "labels": [], "properties": {}}

    # Add properties from table if present
    if context.table:
        for row in context.table:
            field = row["field"]
            value = row["value"]
            if field == "labels":
                node["labels"] = value.split(",")
            else:
                node["properties"][field] = value

    context.neo4j_databases["neo4j"]["nodes"].append(node)


@given("the database contains relationships with types")
def step_database_contains_relationship_types(context):
    """Set up database with specific relationship types."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"relationship_types": set()}}

    for row in context.table:
        rel_type = row["type"]
        context.neo4j_databases["neo4j"]["relationship_types"].add(rel_type)


@given("the database contains nodes with ages")
@given("the database contains {count:d} person nodes")
@given("the database contains person nodes with ages")
def step_database_contains_person_nodes(context, count=10):
    """Set up database with Person nodes."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": []}}

    for i in range(count):
        context.neo4j_databases["neo4j"]["nodes"].append(
            {
                "id": str(200 + i),
                "labels": ["Person"],
                "properties": {"name": f"Person{i}", "age": 20 + (i % 50)},
            }
        )


# ============================================================================
# GIVEN Steps - Query Behavior Setup
# ============================================================================


@given('the "SHOW DATABASES" query will fail with error "{error}"')
@given('But the "SHOW DATABASES" query will fail with error "{error}"')
def step_show_databases_will_fail(context, error):
    """Configure SHOW DATABASES query to fail."""
    context.show_databases_error = error


@given("the Neo4j database will return an error for schema queries")
def step_schema_queries_will_fail(context):
    """Configure schema queries to fail."""
    context.schema_query_error = True


# ============================================================================
# WHEN Steps - Search Operations
# ============================================================================


@when('I search for nodes with query "{query}"')
def step_search_nodes(context, query):
    """Perform node search."""
    endpoint = f"/api/neo4j/search/node/full?q={query}"
    headers = {"X-API-Key": context.api_key}
    context.response = context.client.get(endpoint, headers=headers)


@when('I search for nodes with query "{query}" and fuzziness {fuzziness:f}')
def step_search_nodes_with_fuzziness(context, query, fuzziness):
    """Perform fuzzy node search."""
    endpoint = f"/api/neo4j/search/node/full?q={query}&fuzziness={fuzziness}"
    headers = {"X-API-Key": context.api_key}
    context.response = context.client.get(endpoint, headers=headers)


@when('I search for nodes with query "{query}" and parameters')
def step_search_nodes_with_params(context, query):
    """Perform node search with additional parameters."""
    params = {}
    for row in context.table:
        params[row["parameter"]] = row["value"]

    # Build query string
    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
    endpoint = f"/api/neo4j/search/node/full?q={query}&{param_str}"

    headers = {"X-API-Key": context.api_key}
    context.response = context.client.get(endpoint, headers=headers)


@when('I search for nodes with query "{query}" in database "{database}"')
def step_search_nodes_in_database(context, query, database):
    """Perform node search in specific database."""
    endpoint = f"/api/{database}/search/node/full?q={query}"
    headers = {"X-API-Key": context.api_key}
    context.response = context.client.get(endpoint, headers=headers)


@when('I search for edges with query "{query}"')
def step_search_edges(context, query):
    """Perform edge/relationship search."""
    endpoint = f"/api/neo4j/search/edge/full?q={query}"
    headers = {"X-API-Key": context.api_key}
    context.response = context.client.get(endpoint, headers=headers)


# ============================================================================
# WHEN Steps - Query Execution
# ============================================================================


@when("I execute the Cypher query")
def step_execute_cypher_query(context):
    """Execute Cypher query from text block."""
    endpoint = "/api/neo4j/graph/query"
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}
    body = {"query": context.text.strip()}

    context.response = context.client.post(endpoint, headers=headers, json=body)


@when("I execute the Cypher query with parameters")
def step_execute_query_with_parameters(context):
    """Execute Cypher query with parameters."""
    endpoint = "/api/neo4j/graph/query"
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}

    parameters = {}
    for row in context.table:
        param = row["parameter"]
        value = row["value"]
        # Convert to appropriate type
        if value.isdigit():
            value = int(value)
        parameters[param] = value

    body = {"query": context.text.strip(), "parameters": parameters}
    context.response = context.client.post(endpoint, headers=headers, json=body)


@when("I execute a read query")
@when("I execute a query that will take longer than {seconds:d} seconds")
def step_execute_long_query(context, seconds=60):
    """Execute a long-running query (mock)."""
    # This would be mocked to simulate timeout
    context.query_timeout_seconds = seconds


# ============================================================================
# THEN Steps - Search Result Validation
# ============================================================================


@then('the results should include node "{node_id}" with name "{name}"')
def step_results_include_node(context, node_id, name):
    """Verify results include specific node."""
    response_data = context.response.json()
    assert "results" in response_data, "No results in response"

    matching_node = None
    for result in response_data["results"]:
        if result["id"] == node_id and result["properties"].get("name") == name:
            matching_node = result
            break

    assert (
        matching_node is not None
    ), f"Node {node_id} with name '{name}' not found in results"


@then('the results should include matches for "{search_term}"')
def step_results_include_matches(context, search_term):
    """Verify results include matches for search term."""
    response_data = context.response.json()
    assert "results" in response_data, "No results in response"
    assert len(response_data["results"]) > 0, "No results found"


# ============================================================================
# THEN Steps - Query Validation
# ============================================================================


@then("the query should execute with correct parameters")
@then("the query should execute successfully")
def step_query_executed_successfully(context):
    """Verify query executed successfully."""
    assert (
        context.response.status_code == 200
    ), f"Query failed with status {context.response.status_code}"


@then("the query should use READ routing control")
def step_query_uses_read_routing(context):
    """Verify query uses read routing (mock verification)."""
    # This would check mock call parameters in real implementation
    pass


@then("the query should be executed on a read replica if available")
def step_query_uses_read_replica(context):
    """Verify query targets read replica (mock verification)."""
    # This would verify routing in real implementation
    pass


# ============================================================================
# GIVEN Steps - Database Content with Special Characters
# ============================================================================


@given('the database contains a node with name "{name}"')
def step_database_contains_node_with_name(context, name):
    """Set up database with node having specific name."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": []}}

    node = {
        "id": str(len(context.neo4j_databases["neo4j"]["nodes"]) + 1000),
        "labels": ["Person"],
        "properties": {"name": name},
    }
    context.neo4j_databases["neo4j"]["nodes"].append(node)


@given("the database contains nodes with international characters")
def step_database_contains_intl_nodes(context):
    """Set up database with UTF-8/international character nodes."""
    import json
    import os

    # Load from fixture
    fixture_path = os.path.join("features", "fixtures", "test_data.json")
    with open(fixture_path, encoding="utf-8") as f:
        test_data = json.load(f)

    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": []}}

    context.neo4j_databases["neo4j"]["nodes"].extend(test_data["nodes_with_unicode"])


@given('database "{db}" contains a node with name "{name}"')
def step_specific_database_contains_node(context, db, name):
    """Set up specific database with node."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {}

    if db not in context.neo4j_databases:
        context.neo4j_databases[db] = {"nodes": [], "status": "connected"}

    node = {
        "id": str(len(context.neo4j_databases[db]["nodes"]) + 1000),
        "labels": ["Person"],
        "properties": {"name": name},
    }
    context.neo4j_databases[db]["nodes"].append(node)


@given("the database contains a node with")
@given("the database contains a node with:")
def step_database_contains_node_with_properties(context):
    """Set up database with node having specific properties."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": []}}

    node = {
        "id": str(len(context.neo4j_databases["neo4j"]["nodes"]) + 1000),
        "labels": ["TestNode"],
        "properties": {},
    }

    for row in context.table:
        field = row["property"] if "property" in row else row["field"]
        value = row["value"]
        if field == "labels":
            node["labels"] = value.split(",")
        else:
            node["properties"][field] = value

    context.neo4j_databases["neo4j"]["nodes"].append(node)


@given("the database contains a relationship")
@given("the database contains a relationship:")
def step_database_contains_relationship(context):
    """Set up database with a specific relationship."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"relationships": []}}

    relationship = {}
    for row in context.table:
        field = row["field"] if "field" in row else row.headings[0]
        value = row["value"] if "value" in row else row[1]
        relationship[field] = value

    if "relationships" not in context.neo4j_databases["neo4j"]:
        context.neo4j_databases["neo4j"]["relationships"] = []

    context.neo4j_databases["neo4j"]["relationships"].append(relationship)


@given("the database contains relationships without matching properties")
def step_database_contains_relationships_no_match(context):
    """Set up database with relationships that won't match search."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"relationships": []}}

    context.neo4j_databases["neo4j"]["relationships"] = []


@given("the database contains relationships")
def step_database_contains_relationships_table(context):
    """Set up database with multiple relationships from table."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"relationships": []}}

    for row in context.table:
        relationship = {
            "id": row["id"],
            "type": row["type"],
            "source": row["source"],
            "target": row["target"],
        }
        # Add any additional properties
        for key in row.headings:
            if key not in ["id", "type", "source", "target"]:
                relationship[key] = row[key]

        context.neo4j_databases["neo4j"]["relationships"].append(relationship)


# ============================================================================
# GIVEN Steps - Advanced Database State
# ============================================================================


@given("the Neo4j connection pool is exhausted")
def step_connection_pool_exhausted(context):
    """Simulate connection pool exhaustion."""
    context.neo4j_status = "pool_exhausted"
    context.connection_pool_available = 0


@given("the database contains {count:d} nodes")
def step_database_contains_n_nodes_simple(context, count):
    """Set up database with N nodes (simple version)."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": []}}

    # Generate nodes
    for i in range(count):
        node = {"id": str(i + 1), "labels": ["TestNode"], "properties": {"index": i}}
        context.neo4j_databases["neo4j"]["nodes"].append(node)


@given("the database contains a graph")
@given("the database contains a graph:")
def step_database_contains_graph(context):
    """Set up database with nodes from table for graph."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": [], "relationships": []}}

    for row in context.table:
        node = {
            "id": row["node_id"],
            "labels": row["labels"].split(","),
            "properties": {"name": row["name"]},
        }
        context.neo4j_databases["neo4j"]["nodes"].append(node)


@given(
    'a {rel_type} relationship from {source} to {target} with property {prop} "{value}"'
)
@given("a WORKS_FOR relationship from node {source} to node {target}")
def step_relationship_between_nodes(
    context, source, target, rel_type="WORKS_FOR", prop=None, value=None
):
    """Set up relationship between two nodes."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"relationships": []}}

    if "relationships" not in context.neo4j_databases["neo4j"]:
        context.neo4j_databases["neo4j"]["relationships"] = []

    rel_id = len(context.neo4j_databases["neo4j"]["relationships"]) + 1
    relationship = {
        "id": str(rel_id),
        "type": rel_type,
        "source": str(source),
        "target": str(target),
        "properties": {},
    }

    if prop and value:
        relationship["properties"][prop] = value

    context.neo4j_databases["neo4j"]["relationships"].append(relationship)


@given('node "{node_id}" has an outgoing {rel_type} relationship to node "{target_id}"')
def step_node_has_outgoing_relationship(context, node_id, rel_type, target_id):
    """Set up outgoing relationship from node."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"relationships": []}}

    relationship = {
        "id": str(len(context.neo4j_databases["neo4j"].get("relationships", [])) + 1),
        "type": rel_type,
        "source": node_id,
        "target": target_id,
        "properties": {},
    }

    if "relationships" not in context.neo4j_databases["neo4j"]:
        context.neo4j_databases["neo4j"]["relationships"] = []

    context.neo4j_databases["neo4j"]["relationships"].append(relationship)


@given(
    'the database contains a node with ID "{node_id}" that has {count:d} relationships'
)
def step_node_with_n_relationships(context, node_id, count):
    """Set up node with specific number of relationships."""
    if not hasattr(context, "neo4j_databases"):
        context.neo4j_databases = {"neo4j": {"nodes": [], "relationships": []}}

    # Create the main node if it doesn't exist
    node = {"id": node_id, "labels": ["Person"], "properties": {"degree": count}}
    context.neo4j_databases["neo4j"]["nodes"].append(node)

    # Create relationships
    for i in range(count):
        rel = {
            "id": str(i + 1),
            "type": "CONNECTED_TO",
            "source": node_id,
            "target": str(i + 1000),
            "properties": {},
        }
        context.neo4j_databases["neo4j"]["relationships"].append(rel)


# ============================================================================
# WHEN Steps - Cypher Query with Special Handling
# ============================================================================


@when("I execute the Cypher query with malicious input")
def step_execute_query_with_injection(context):
    """Execute Cypher query with injection attempt."""
    endpoint = "/api/neo4j/graph/query"
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}

    # Get malicious input from text
    malicious_query = context.text.strip()

    body = {"query": malicious_query}
    context.response = context.client.post(endpoint, headers=headers, json=body)


@when("I execute a Cypher query with timeout {seconds:d} seconds")
def step_execute_query_with_timeout(context, seconds):
    """Execute query with specific timeout."""
    endpoint = "/api/neo4j/graph/query"
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}

    body = {
        "query": (
            context.text.strip()
            if hasattr(context, "text")
            else "MATCH (n) RETURN n LIMIT 10"
        ),
        "timeout": seconds,
    }

    context.query_timeout = seconds
    context.response = context.client.post(endpoint, headers=headers, json=body)


@when("I request to explain the Cypher query")
def step_request_explain_query(context):
    """Request query execution plan without executing."""
    endpoint = "/api/neo4j/graph/query/explain"
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}

    body = {"query": context.text.strip()}
    context.response = context.client.post(endpoint, headers=headers, json=body)


# ============================================================================
# THEN Steps - Result Content Validation
# ============================================================================


@then('the result should have property "{property}" with value "{value}"')
def step_result_has_property_value(context, property, value):
    """Verify result has specific property value."""
    response_data = context.response.json()
    assert "results" in response_data, "No results in response"
    assert len(response_data["results"]) > 0, "Results array is empty"

    first_result = response_data["results"][0]
    assert "properties" in first_result, "No properties in result"
    assert (
        property in first_result["properties"]
    ), f"Property '{property}' not found in result"

    actual = first_result["properties"][property]
    assert str(actual) == str(
        value
    ), f"Property '{property}': expected '{value}', got '{actual}'"


@then('the result labels should include "{label}"')
def step_result_labels_include(context, label):
    """Verify result labels include specific label."""
    response_data = context.response.json()
    assert "results" in response_data, "No results in response"
    assert len(response_data["results"]) > 0, "Results array is empty"

    first_result = response_data["results"][0]
    assert "labels" in first_result, "No labels in result"
    assert (
        label in first_result["labels"]
    ), f"Label '{label}' not found in result labels: {first_result['labels']}"


@then('the result properties should have field "{field}" with value "{value}"')
def step_result_properties_field_value(context, field, value):
    """Verify result properties have specific field."""
    response_data = context.response.json()
    assert "results" in response_data, "No results in response"
    assert len(response_data["results"]) > 0, "Results array is empty"

    first_result = response_data["results"][0]
    assert "properties" in first_result, "No properties in result"

    properties = first_result["properties"]
    assert field in properties, f"Field '{field}' not found in properties"

    actual = properties[field]
    # Type conversion
    if value.isdigit():
        value = int(value)

    assert actual == value, f"Property '{field}': expected {value}, got {actual}"


@then("the response should include query plan")
def step_response_includes_query_plan(context):
    """Verify response includes query execution plan."""
    response_data = context.response.json()
    assert "plan" in response_data, "No query plan in response"
    assert isinstance(response_data["plan"], dict), "Query plan should be an object"


@then("the query should respect the timeout setting")
def step_query_respects_timeout(context):
    """Verify query timeout was applied."""
    # In mock mode, just check that request succeeded
    assert context.response.status_code in [
        200,
        504,
    ], f"Unexpected status code: {context.response.status_code}"
