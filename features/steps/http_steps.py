"""
HTTP request/response step definitions for behave BDD tests.
"""

import json
import time
from behave import given, when, then, step
from behave.model import Table
import re


# ============================================================================
# WHEN Steps - HTTP Requests
# ============================================================================

@when('I send a {method} request to "{endpoint}"')
def step_send_request(context, method, endpoint):
    """Send HTTP request without authentication."""
    context.start_time = time.time()

    if method.upper() == 'GET':
        context.response = context.client.get(endpoint)
    elif method.upper() == 'POST':
        context.response = context.client.post(endpoint)
    elif method.upper() == 'PUT':
        context.response = context.client.put(endpoint)
    elif method.upper() == 'DELETE':
        context.response = context.client.delete(endpoint)

    context.end_time = time.time()


@when('I send a {method} request to "{endpoint}" with authentication')
def step_send_authenticated_request(context, method, endpoint):
    """Send HTTP request with API key authentication."""
    headers = {"X-API-Key": context.api_key}
    context.start_time = time.time()

    if method.upper() == 'GET':
        context.response = context.client.get(endpoint, headers=headers)
    elif method.upper() == 'POST':
        context.response = context.client.post(endpoint, headers=headers)
    elif method.upper() == 'PUT':
        context.response = context.client.put(endpoint, headers=headers)
    elif method.upper() == 'DELETE':
        context.response = context.client.delete(endpoint, headers=headers)

    context.end_time = time.time()


@when('I send a {method} request to "{endpoint}" without authentication')
def step_send_unauthenticated_request(context, method, endpoint):
    """Send HTTP request explicitly without authentication."""
    context.start_time = time.time()

    if method.upper() == 'GET':
        context.response = context.client.get(endpoint)
    elif method.upper() == 'POST':
        context.response = context.client.post(endpoint)

    context.end_time = time.time()


@when('I send a {method} request to "{endpoint}" with headers')
def step_send_request_with_headers(context, method, endpoint):
    """Send HTTP request with custom headers from table."""
    headers = {}
    for row in context.table:
        headers[row['header']] = row['value']

    context.start_time = time.time()

    if method.upper() == 'GET':
        context.response = context.client.get(endpoint, headers=headers)
    elif method.upper() == 'POST':
        context.response = context.client.post(endpoint, headers=headers)

    context.end_time = time.time()


@when('I send a {method} request to "{endpoint}" with authentication and body')
def step_send_request_with_body(context, method, endpoint):
    """Send HTTP request with authentication and JSON body."""
    headers = {"X-API-Key": context.api_key, "Content-Type": "application/json"}
    body = json.loads(context.text)

    context.start_time = time.time()

    if method.upper() == 'POST':
        context.response = context.client.post(endpoint, headers=headers, json=body)
    elif method.upper() == 'PUT':
        context.response = context.client.put(endpoint, headers=headers, json=body)

    context.end_time = time.time()


# ============================================================================
# THEN Steps - Response Status
# ============================================================================

@then('the response status code should be {status_code:d}')
def step_check_status_code(context, status_code):
    """Verify HTTP response status code."""
    assert context.response.status_code == status_code, \
        f"Expected status {status_code}, got {context.response.status_code}. Response: {context.response.text}"


@then('the response status code should not be {status_code:d}')
def step_check_status_code_not(context, status_code):
    """Verify HTTP response status code is not a specific value."""
    assert context.response.status_code != status_code, \
        f"Status code should not be {status_code}, but it was"


# ============================================================================
# THEN Steps - Response Time
# ============================================================================

@then('the response time should be less than {milliseconds:d} milliseconds')
def step_check_response_time(context, milliseconds):
    """Verify response time is within threshold."""
    elapsed_ms = (context.end_time - context.start_time) * 1000
    assert elapsed_ms < milliseconds, \
        f"Response took {elapsed_ms:.2f}ms, expected < {milliseconds}ms"


# ============================================================================
# THEN Steps - JSON Response Validation
# ============================================================================

@then('the JSON response should contain')
def step_check_json_contains_table(context):
    """Verify JSON response contains expected field/value pairs from table."""
    response_data = context.response.json()

    for row in context.table:
        field = row['field']
        expected_value = row['value']

        assert field in response_data, \
            f"Field '{field}' not found in response: {response_data}"

        actual_value = str(response_data[field])
        assert actual_value == expected_value, \
            f"Field '{field}': expected '{expected_value}', got '{actual_value}'"


@then('the JSON response should have field "{field}" with value "{value}"')
def step_check_json_field_value(context, field, value):
    """Verify JSON response has specific field with value."""
    response_data = context.response.json()

    # Navigate nested fields (e.g., "data.name")
    fields = field.split('.')
    current = response_data
    for f in fields:
        assert f in current, f"Field '{f}' not found in {current}"
        current = current[f]

    # Convert value to appropriate type
    if value.lower() == 'true':
        expected = True
    elif value.lower() == 'false':
        expected = False
    elif value.isdigit():
        expected = int(value)
    else:
        expected = value

    assert current == expected, \
        f"Field '{field}': expected {expected}, got {current}"


@then('the JSON response should have a "{field}" {field_type}')
@then('the JSON response should have field "{field}" as an {field_type}')
@then('the JSON response should have field "{field}" as a {field_type}')
def step_check_json_field_type(context, field, field_type):
    """Verify JSON response has field of specific type."""
    response_data = context.response.json()

    assert field in response_data, f"Field '{field}' not found in response"

    actual = response_data[field]

    if field_type in ['array', 'list']:
        assert isinstance(actual, list), \
            f"Field '{field}' should be array, got {type(actual)}"
    elif field_type == 'object':
        assert isinstance(actual, dict), \
            f"Field '{field}' should be object, got {type(actual)}"
    elif field_type == 'string':
        assert isinstance(actual, str), \
            f"Field '{field}' should be string, got {type(actual)}"
    elif field_type in ['number', 'integer']:
        assert isinstance(actual, (int, float)), \
            f"Field '{field}' should be number, got {type(actual)}"
    elif field_type == 'boolean':
        assert isinstance(actual, bool), \
            f"Field '{field}' should be boolean, got {type(actual)}"


@then('the response should contain an "{field}" field')
@then('the response should have field "{field}"')
def step_check_field_exists(context, field):
    """Verify response contains a specific field."""
    response_data = context.response.json()

    # Navigate nested fields
    fields = field.split('.')
    current = response_data
    for f in fields:
        assert f in current, \
            f"Field '{f}' not found in {current}"
        current = current[f]


@then('the response should contain {count:d} results')
@then('the response should contain {count:d} result')
def step_check_result_count(context, count):
    """Verify response contains expected number of results."""
    response_data = context.response.json()
    assert 'results' in response_data, "No 'results' field in response"

    actual_count = len(response_data['results'])
    assert actual_count == count, \
        f"Expected {count} results, got {actual_count}"


@then('the results array should be empty')
def step_check_results_empty(context):
    """Verify results array is empty."""
    response_data = context.response.json()
    assert 'results' in response_data, "No 'results' field in response"
    assert len(response_data['results']) == 0, \
        f"Expected empty results, got {len(response_data['results'])} items"


# ============================================================================
# THEN Steps - Error Response Validation
# ============================================================================

@then('the JSON response should have an "{field}" object')
def step_check_error_object(context, field):
    """Verify response has error object."""
    response_data = context.response.json()
    assert field in response_data, f"No '{field}' field in response"
    assert isinstance(response_data[field], dict), \
        f"'{field}' should be an object"


@then('the error code should be "{code}"')
def step_check_error_code(context, code):
    """Verify error code in response."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error object in response"
    assert 'code' in response_data['error'], "No error code in response"

    assert response_data['error']['code'] == code, \
        f"Expected error code '{code}', got '{response_data['error']['code']}'"


@then('the error message should contain "{text}"')
def step_check_error_message_contains(context, text):
    """Verify error message contains specific text."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error object in response"
    assert 'message' in response_data['error'], "No error message in response"

    message = response_data['error']['message']
    assert text in message, \
        f"Expected error message to contain '{text}', got '{message}'"


@then('the error details should include')
@then('the error details should have')
def step_check_error_details_table(context):
    """Verify error details contain expected fields from table."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error object in response"
    assert 'details' in response_data['error'], "No error details in response"

    details = response_data['error']['details']
    for row in context.table:
        field = row['field']
        expected_value = row['value']

        assert field in details, f"Field '{field}' not in error details"
        assert str(details[field]) == expected_value, \
            f"Error detail '{field}': expected '{expected_value}', got '{details[field]}'"


@then('the error details should have field "{field}" with value "{value}"')
def step_check_error_detail_field(context, field, value):
    """Verify error details has specific field with value."""
    response_data = context.response.json()
    assert 'error' in response_data, "No error object in response"
    assert 'details' in response_data['error'], "No error details in response"

    details = response_data['error']['details']
    assert field in details, f"Field '{field}' not in error details"

    actual_value = str(details[field])
    assert actual_value == value, \
        f"Error detail '{field}': expected '{value}', got '{actual_value}'"
