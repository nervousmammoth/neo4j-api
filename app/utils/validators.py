"""Query validation utilities.

This module provides read-only query validation to ensure no write
operations (CREATE, DELETE, MERGE, SET, REMOVE) are executed.
"""

from __future__ import annotations

import re
from re import Pattern

# Combined write keywords pattern for performance
# A single combined pattern is more performant than a list of patterns
_WRITE_KEYWORDS_PATTERN = (
    r"\b(CREATE|DELETE|MERGE|SET|REMOVE|DROP)\b|\bDETACH\s+DELETE\b"
)

# Compile the single pattern for performance
WRITE_PATTERN: Pattern[str] = re.compile(_WRITE_KEYWORDS_PATTERN, re.IGNORECASE)


def _remove_comments(query: str) -> str:
    """Remove comments from Cypher query.

    Args:
        query: Cypher query string.

    Returns:
        Query with comments removed.
    """
    # Remove single-line comments
    query = re.sub(r"//.*?$", "", query, flags=re.MULTILINE)
    # Remove multi-line comments
    query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
    return query


def _remove_string_literals(query: str) -> str:
    """Remove string literals from query.

    This prevents false positives from keywords inside strings.
    Handles escaped quotes within strings to prevent bypass attacks.

    Args:
        query: Cypher query string.

    Returns:
        Query with string literals removed.
    """
    # Remove single-quoted strings (handles escaped quotes like \')
    query = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "", query)
    # Remove double-quoted strings (handles escaped quotes like \")
    query = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', "", query)
    return query


def is_read_only_query(query: str) -> bool:
    """Check if a Cypher query is read-only.

    This function validates that the query does not contain any write
    operations such as CREATE, DELETE, MERGE, SET, REMOVE, or DROP.

    Args:
        query: Cypher query string to validate.

    Returns:
        True if query is read-only, False if write operations detected.

    Examples:
        >>> is_read_only_query("MATCH (n) RETURN n")
        True
        >>> is_read_only_query("CREATE (n:Person) RETURN n")
        False
        >>> is_read_only_query("MATCH (n) SET n.name = 'John'")
        False
    """
    if not query or not query.strip():
        return True  # Empty query is considered safe

    # Remove comments and string literals to avoid false positives
    cleaned_query = _remove_comments(query)
    cleaned_query = _remove_string_literals(cleaned_query)

    # Check for write keywords - return True if no write patterns found
    return not WRITE_PATTERN.search(cleaned_query)
