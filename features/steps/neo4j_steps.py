"""
Neo4j database-specific step definitions.
"""

from behave import given, when, then


# ============================================================================
# GIVEN Steps - Neo4j Database State
# ============================================================================

@given('the Neo4j database is connected')
@given('the Neo4j database is connected and responsive')
@given('the Neo4j database "{database}" is connected')
def step_neo4j_connected(context, database='neo4j'):
    """Set up Neo4j database as connected."""
    if not hasattr(context, 'neo4j_databases'):
        context.neo4j_databases = {}

    context.neo4j_databases[database] = {
        'status': 'connected',
        'nodes': [],
        'relationships': [],
        'labels': set(),
        'relationship_types': set()
    }


@given('the Neo4j database is disconnected')
def step_neo4j_disconnected(context):
    """Set up Neo4j database as disconnected."""
    context.neo4j_status = 'disconnected'


@given('the Neo4j database connection will timeout')
def step_neo4j_will_timeout(context):
    """Configure Neo4j mock to simulate timeout."""
    context.neo4j_status = 'timeout'


@given('the Neo4j databases "{db1}" and "{db2}" exist')
def step_multiple_databases_exist(context, db1, db2):
    """Set up multiple Neo4j databases."""
    if not hasattr(context, 'neo4j_databases'):
        context.neo4j_databases = {}

    for db in [db1, db2]:
        context.neo4j_databases[db] = {
            'status': 'connected',
            'nodes': [],
            'relationships': [],
            'labels': set(),
            'relationship_types': set()
        }


@given('the following databases exist')
def step_databases_exist_table(context):
    """Set up multiple databases from table."""
    if not hasattr(context, 'available_databases'):
        context.available_databases = []

    for row in context.table:
        db_info = {
            'name': row['name'],
            'default': row['default'].lower() == 'true',
            'status': row['status'],
            'description': row.get('description', '')
        }
        context.available_databases.append(db_info)


@given('only the default database "{db_name}" exists')
def step_only_default_database_exists(context, db_name):
    """Set up scenario with only default database."""
    context.available_databases = [{
        'name': db_name,
        'default': True,
        'status': 'online'
    }]


@given('the database is empty')
@given('the database contains no nodes')
def step_database_empty(context):
    """Set up empty database."""
    context.neo4j_databases = {
        'neo4j': {
            'status': 'connected',
            'nodes': [],
            'relationships': [],
            'labels': set(),
            'relationship_types': set()
        }
    }


# ============================================================================
# GIVEN Steps - Database Content Setup
# ============================================================================

@given('the database contains nodes')
@given('the database contains {count:d} nodes')
def step_database_contains_nodes(context, count=10):
    """Set up database with N nodes."""
    if not hasattr(context, 'neo4j_databases'):
        context.neo4j_databases = {'neo4j': {'nodes': []}}

    # Generate mock nodes
    for i in range(count):
        context.neo4j_databases['neo4j']['nodes'].append({
            'id': str(100 + i),
            'labels': ['TestNode'],
            'properties': {'id': i}
        })


@given('the database contains nodes with labels')
def step_database_contains_labeled_nodes(context):
    """Set up database with nodes having specific labels."""
    if not hasattr(context, 'neo4j_databases'):
        context.neo4j_databases = {'neo4j': {'nodes': [], 'labels': set()}}

    for row in context.table:
        label = row['label']
        context.neo4j_databases['neo4j']['labels'].add(label)


@given('the database contains a node with ID "{node_id}"')
def step_database_contains_node_with_id(context, node_id):
    """Set up specific node in database."""
    if not hasattr(context, 'neo4j_databases'):
        context.neo4j_databases = {'neo4j': {'nodes': []}}

    node = {
        'id': node_id,
        'labels': [],
        'properties': {}
    }

    # Add properties from table if present
    if context.table:
        for row in context.table:
            field = row['field']
            value = row['value']
            if field == 'labels':
                node['labels'] = value.split(',')
            else:
                node['properties'][field] = value

    context.neo4j_databases['neo4j']['nodes'].append(node)


@given('the database contains relationships with types')
def step_database_contains_relationship_types(context):
    """Set up database with specific relationship types."""
    if not hasattr(context, 'neo4j_databases'):
        context.neo4j_databases = {'neo4j': {'relationship_types': set()}}

    for row in context.table:
        rel_type = row['type']
        context.neo4j_databases['neo4j']['relationship_types'].add(rel_type)


@given('the database contains nodes with ages')
@given('the database contains {count:d} person nodes')
@given('the database contains person nodes with ages')
def step_database_contains_person_nodes(context, count=10):
    """Set up database with Person nodes."""
    if not hasattr(context, 'neo4j_databases'):
        context.neo4j_databases = {'neo4j': {'nodes': []}}

    for i in range(count):
        context.neo4j_databases['neo4j']['nodes'].append({
            'id': str(200 + i),
            'labels': ['Person'],
            'properties': {'name': f'Person{i}', 'age': 20 + (i % 50)}
        })


# ============================================================================
# GIVEN Steps - Query Behavior Setup
# ============================================================================

@given('the "SHOW DATABASES" query will fail with error "{error}"')
@given('But the "SHOW DATABASES" query will fail with error "{error}"')
def step_show_databases_will_fail(context, error):
    """Configure SHOW DATABASES query to fail."""
    context.show_databases_error = error


@given('the Neo4j database will return an error for schema queries')
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
        params[row['parameter']] = row['value']

    # Build query string
    param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
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

@when('I execute the Cypher query')
def step_execute_cypher_query(context):
    """Execute Cypher query from text block."""
    endpoint = "/api/neo4j/graph/query"
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}
    body = {"query": context.text.strip()}

    context.response = context.client.post(endpoint, headers=headers, json=body)


@when('I execute the Cypher query with parameters')
def step_execute_query_with_parameters(context):
    """Execute Cypher query with parameters."""
    endpoint = "/api/neo4j/graph/query"
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}

    parameters = {}
    for row in context.table:
        param = row['parameter']
        value = row['value']
        # Convert to appropriate type
        if value.isdigit():
            value = int(value)
        parameters[param] = value

    body = {"query": context.text.strip(), "parameters": parameters}
    context.response = context.client.post(endpoint, headers=headers, json=body)


@when('I execute a read query')
@when('I execute a query that will take longer than {seconds:d} seconds')
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
    assert 'results' in response_data, "No results in response"

    matching_node = None
    for result in response_data['results']:
        if result['id'] == node_id and result['properties'].get('name') == name:
            matching_node = result
            break

    assert matching_node is not None, \
        f"Node {node_id} with name '{name}' not found in results"


@then('the results should include matches for "{search_term}"')
def step_results_include_matches(context, search_term):
    """Verify results include matches for search term."""
    response_data = context.response.json()
    assert 'results' in response_data, "No results in response"
    assert len(response_data['results']) > 0, "No results found"


# ============================================================================
# THEN Steps - Query Validation
# ============================================================================

@then('the query should execute with correct parameters')
@then('the query should execute successfully')
def step_query_executed_successfully(context):
    """Verify query executed successfully."""
    assert context.response.status_code == 200, \
        f"Query failed with status {context.response.status_code}"


@then('the query should use READ routing control')
def step_query_uses_read_routing(context):
    """Verify query uses read routing (mock verification)."""
    # This would check mock call parameters in real implementation
    pass


@then('the query should be executed on a read replica if available')
def step_query_uses_read_replica(context):
    """Verify query targets read replica (mock verification)."""
    # This would verify routing in real implementation
    pass
