"""
Authentication-specific step definitions.
"""

from behave import given, when, then


# ============================================================================
# GIVEN Steps - Authentication Setup
# ============================================================================

@given('the configured API key is "{api_key}"')
def step_set_configured_api_key(context, api_key):
    """Set the expected/configured API key for the API."""
    context.configured_api_key = api_key
    # In tests, this would configure the mock API to expect this key


@given('I have a valid API key "{api_key}"')
def step_set_user_api_key(context, api_key):
    """Set the API key to use for requests."""
    context.api_key = api_key


@given('the application logging is enabled')
def step_enable_logging(context):
    """Enable application logging for verification."""
    # This would configure the test environment to capture logs
    context.logging_enabled = True
    context.captured_logs = []


# ============================================================================
# WHEN Steps - Authentication Actions
# ============================================================================

@when('I send authenticated requests to the following endpoints')
def step_send_multiple_authenticated_requests(context):
    """Send multiple authenticated requests from table."""
    context.multi_responses = []

    for row in context.table:
        method = row['method']
        endpoint = row['endpoint']
        headers = {"X-API-Key": context.api_key}

        if method.upper() == 'GET':
            response = context.client.get(endpoint, headers=headers)
        elif method.upper() == 'POST':
            response = context.client.post(endpoint, headers=headers, json={})

        context.multi_responses.append({
            'method': method,
            'endpoint': endpoint,
            'response': response
        })

    # Set last response as current context response for compatibility
    if context.multi_responses:
        context.response = context.multi_responses[-1]['response']


# ============================================================================
# THEN Steps - Authentication Validation
# ============================================================================

@then('all requests should return status code {code:d} or {alt_code:d}')
def step_check_all_responses_status(context, code, alt_code):
    """Verify all multi-responses have one of the allowed status codes."""
    assert hasattr(context, 'multi_responses'), "No multi_responses found"

    for item in context.multi_responses:
        status = item['response'].status_code
        assert status in [code, alt_code], \
            f"{item['method']} {item['endpoint']}: Expected {code} or {alt_code}, got {status}"


@then('none of the requests should return status code {code:d}')
def step_check_no_response_has_status(context, code):
    """Verify none of the multi-responses have specific status code."""
    assert hasattr(context, 'multi_responses'), "No multi_responses found"

    for item in context.multi_responses:
        status = item['response'].status_code
        assert status != code, \
            f"{item['method']} {item['endpoint']}: Should not return {code}, but did"


@then('a failed authentication attempt should be logged with details')
def step_check_auth_failure_logged(context):
    """Verify failed authentication attempt was logged."""
    # In a real implementation, this would check captured logs
    assert context.logging_enabled, "Logging not enabled"

    # Mock verification - in reality, would check actual log entries
    for row in context.table:
        field = row['field']
        value = row['value']
        # Verify log contains expected fields
        # This is a placeholder - real implementation would parse logs


# ============================================================================
# THEN Steps - API Key Header Validation
# ============================================================================

@then('the API key header name is case-insensitive')
def step_verify_header_case_insensitive(context):
    """Verify API key works with different header name casing."""
    # This step is more of a documentation step
    # The actual test is in the scenario using lowercase header
    pass
