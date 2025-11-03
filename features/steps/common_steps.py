"""
Common step definitions shared across all features.
"""

from behave import given, when, then


# ============================================================================
# GIVEN Steps - Test Setup
# ============================================================================

@given('the API is running')
def step_api_is_running(context):
    """
    Ensure the test API client is ready.
    The actual setup is done in environment.py before_scenario.
    """
    assert hasattr(context, 'client'), "Test client not initialized"
    assert hasattr(context, 'api_key'), "API key not set"


@given('I have a valid API key')
def step_have_valid_api_key(context):
    """Set up valid API key for authenticated requests."""
    # API key is set in environment.py, just verify it exists
    assert hasattr(context, 'api_key'), "API key not configured"
    assert context.api_key is not None, "API key is None"


# ============================================================================
# THEN Steps - Array Validation
# ============================================================================

@then('the "{array_name}" array should contain {count:d} items')
@then('the "{array_name}" array should contain {count:d} item')
def step_check_array_count(context, array_name, count):
    """Verify array contains expected number of items."""
    response_data = context.response.json()

    assert array_name in response_data, \
        f"Array '{array_name}' not found in response"

    actual_count = len(response_data[array_name])
    assert actual_count == count, \
        f"Expected {count} items in '{array_name}', got {actual_count}"


@then('the "{array_name}" array should contain at least {count:d} items')
@then('the "{array_name}" array should contain at least {count:d} item')
def step_check_array_min_count(context, array_name, count):
    """Verify array contains at least N items."""
    response_data = context.response.json()

    assert array_name in response_data, \
        f"Array '{array_name}' not found in response"

    actual_count = len(response_data[array_name])
    assert actual_count >= count, \
        f"Expected at least {count} items in '{array_name}', got {actual_count}"


@then('the "{array_name}" array should not exceed {count:d} items')
def step_check_array_max_count(context, array_name, count):
    """Verify array does not exceed maximum count."""
    response_data = context.response.json()

    assert array_name in response_data, \
        f"Array '{array_name}' not found in response"

    actual_count = len(response_data[array_name])
    assert actual_count <= count, \
        f"Expected at most {count} items in '{array_name}', got {actual_count}"


@then('the "{array_name}" array should be empty')
def step_check_array_empty(context, array_name):
    """Verify array is empty."""
    response_data = context.response.json()

    assert array_name in response_data, \
        f"Array '{array_name}' not found in response"

    assert len(response_data[array_name]) == 0, \
        f"Expected empty array, got {len(response_data[array_name])} items"


@then('the "{array_name}" array should contain "{value}"')
def step_check_array_contains(context, array_name, value):
    """Verify array contains a specific value."""
    response_data = context.response.json()

    assert array_name in response_data, \
        f"Array '{array_name}' not found in response"

    array = response_data[array_name]
    assert value in array, \
        f"Value '{value}' not found in array '{array_name}': {array}"


@then('the types array should be sorted alphabetically')
@then('the "{array_name}" array should be sorted alphabetically')
def step_check_array_sorted(context, array_name='types'):
    """Verify array is sorted alphabetically."""
    response_data = context.response.json()

    assert array_name in response_data, \
        f"Array '{array_name}' not found in response"

    array = response_data[array_name]
    sorted_array = sorted(array)

    assert array == sorted_array, \
        f"Array is not sorted. Got: {array}, Expected: {sorted_array}"


# ============================================================================
# THEN Steps - Field/Property Validation
# ============================================================================

@then('the first result should have property "{property}" with value "{value}"')
def step_check_first_result_property(context, property, value):
    """Check property value in first result."""
    response_data = context.response.json()
    assert 'results' in response_data, "No results in response"
    assert len(response_data['results']) > 0, "Results array is empty"

    first_result = response_data['results'][0]
    assert 'properties' in first_result, "No properties in first result"
    assert property in first_result['properties'], \
        f"Property '{property}' not found"

    actual = first_result['properties'][property]
    # Type conversion for comparison
    if value.isdigit():
        value = int(value)

    assert actual == value, \
        f"Expected '{property}' to be '{value}', got '{actual}'"


@then('all databases should have required fields')
def step_check_all_databases_have_fields(context):
    """Verify all database objects have required fields."""
    response_data = context.response.json()
    assert 'databases' in response_data, "No databases in response"

    for row in context.table:
        field_name = row['field']
        for db in response_data['databases']:
            assert field_name in db, \
                f"Database missing required field '{field_name}': {db}"


# ============================================================================
# THEN Steps - Specific Content Validation
# ============================================================================

@then('the database "{db_name}" should be marked as default')
def step_check_database_is_default(context, db_name):
    """Verify specific database is marked as default."""
    response_data = context.response.json()
    assert 'databases' in response_data, "No databases in response"

    databases = response_data['databases']
    target_db = next((db for db in databases if db['name'] == db_name), None)

    assert target_db is not None, \
        f"Database '{db_name}' not found in response"
    assert target_db.get('default') is True, \
        f"Database '{db_name}' is not marked as default"


@then('the "{array_name}" array should include database "{db_name}"')
def step_check_array_includes_database(context, array_name, db_name):
    """Verify array includes a specific database by name."""
    response_data = context.response.json()
    assert array_name in response_data, f"Array '{array_name}' not found"

    databases = response_data[array_name]
    db_names = [db['name'] for db in databases if isinstance(db, dict)]

    assert db_name in db_names, \
        f"Database '{db_name}' not found in {array_name}"


@then('the validation errors should include field "{field}"')
def step_check_validation_error_field(context, field):
    """Verify validation errors include a specific field."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error in response"
    assert 'details' in response_data['error'], "No error details"
    assert 'errors' in response_data['error']['details'], "No validation errors"

    errors = response_data['error']['details']['errors']
    error_fields = [err.get('field') for err in errors]

    assert field in error_fields, \
        f"Field '{field}' not in validation errors: {error_fields}"


@then('the error should indicate invalid parameter "{param}"')
def step_check_invalid_parameter(context, param):
    """Verify error message indicates invalid parameter."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error in response"

    # Check if error message or details mention the parameter
    error_str = str(response_data['error'])
    assert param in error_str, \
        f"Parameter '{param}' not mentioned in error: {error_str}"


@then('the error should indicate service unavailability')
def step_check_service_unavailable_error(context):
    """Verify error indicates service is unavailable."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error in response"

    error_message = response_data['error'].get('message', '').lower()
    assert any(word in error_message for word in ['unavailable', 'disconnected', 'down']), \
        f"Error doesn't indicate service unavailability: {error_message}"


# ============================================================================
# THEN Steps - Metadata Validation
# ============================================================================

@then('the error details should list allowed operations')
def step_check_allowed_operations_listed(context):
    """Verify error details list allowed operations."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error in response"
    assert 'details' in response_data['error'], "No error details"

    details = response_data['error']['details']
    assert 'allowed_operations' in details, \
        "No allowed_operations in error details"
    assert isinstance(details['allowed_operations'], list), \
        "allowed_operations should be a list"
    assert len(details['allowed_operations']) > 0, \
        "allowed_operations list is empty"
