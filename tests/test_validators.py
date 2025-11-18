"""Unit tests for query validation utilities.

This module tests the read-only query validator to ensure it correctly
blocks write operations and allows read-only queries.
"""

from __future__ import annotations

from app.utils.validators import is_read_only_query


class TestIsReadOnlyQueryAllowed:
    """Test cases for queries that should be allowed."""

    def test_simple_match_query(self) -> None:
        """MATCH queries should be allowed."""
        query = "MATCH (n) RETURN n"
        assert is_read_only_query(query) is True

    def test_match_with_where_clause(self) -> None:
        """MATCH queries with WHERE should be allowed."""
        query = "MATCH (n:Person) WHERE n.age > 30 RETURN n"
        assert is_read_only_query(query) is True

    def test_match_with_relationships(self) -> None:
        """MATCH queries with relationships should be allowed."""
        query = "MATCH (n)-[r:KNOWS]->(m) RETURN n, r, m"
        assert is_read_only_query(query) is True

    def test_optional_match(self) -> None:
        """OPTIONAL MATCH should be allowed."""
        query = "OPTIONAL MATCH (n)-[r]-(m) RETURN n, r, m"
        assert is_read_only_query(query) is True

    def test_with_clause(self) -> None:
        """WITH clause should be allowed."""
        query = "MATCH (n) WITH n MATCH (n)-[r]->(m) RETURN n, r, m"
        assert is_read_only_query(query) is True

    def test_call_db_labels(self) -> None:
        """CALL db.* procedures should be allowed."""
        query = "CALL db.labels() YIELD label RETURN label"
        assert is_read_only_query(query) is True

    def test_call_db_relationship_types(self) -> None:
        """CALL db.relationshipTypes should be allowed."""
        query = "CALL db.relationshipTypes()"
        assert is_read_only_query(query) is True

    def test_show_databases(self) -> None:
        """SHOW commands should be allowed."""
        query = "SHOW DATABASES"
        assert is_read_only_query(query) is True

    def test_unwind_clause(self) -> None:
        """UNWIND should be allowed."""
        query = "UNWIND [1, 2, 3] AS x RETURN x"
        assert is_read_only_query(query) is True

    def test_empty_query(self) -> None:
        """Empty query should be considered safe."""
        assert is_read_only_query("") is True

    def test_whitespace_only_query(self) -> None:
        """Query with only whitespace should be considered safe."""
        assert is_read_only_query("   \n  \t  ") is True


class TestIsReadOnlyQueryBlocked:
    """Test cases for queries that should be blocked."""

    def test_create_node_blocked(self) -> None:
        """CREATE queries should be blocked."""
        query = "CREATE (n:Person) RETURN n"
        assert is_read_only_query(query) is False

    def test_create_relationship_blocked(self) -> None:
        """CREATE with relationships should be blocked."""
        query = "MATCH (a), (b) CREATE (a)-[r:KNOWS]->(b) RETURN r"
        assert is_read_only_query(query) is False

    def test_delete_blocked(self) -> None:
        """DELETE queries should be blocked."""
        query = "MATCH (n) DELETE n"
        assert is_read_only_query(query) is False

    def test_detach_delete_blocked(self) -> None:
        """DETACH DELETE should be blocked."""
        query = "MATCH (n) DETACH DELETE n"
        assert is_read_only_query(query) is False

    def test_merge_blocked(self) -> None:
        """MERGE queries should be blocked."""
        query = "MERGE (n:Person {id: 1}) RETURN n"
        assert is_read_only_query(query) is False

    def test_set_property_blocked(self) -> None:
        """SET queries should be blocked."""
        query = "MATCH (n) SET n.name = 'John' RETURN n"
        assert is_read_only_query(query) is False

    def test_remove_property_blocked(self) -> None:
        """REMOVE queries should be blocked."""
        query = "MATCH (n) REMOVE n.age RETURN n"
        assert is_read_only_query(query) is False

    def test_drop_index_blocked(self) -> None:
        """DROP queries should be blocked."""
        query = "DROP INDEX index_name"
        assert is_read_only_query(query) is False


class TestIsReadOnlyQueryEdgeCases:
    """Test cases for edge cases and security scenarios."""

    def test_mixed_case_create_blocked(self) -> None:
        """CREATE in mixed case should be blocked."""
        query = "CrEaTe (n:Person) RETURN n"
        assert is_read_only_query(query) is False

    def test_mixed_case_match_allowed(self) -> None:
        """MATCH in mixed case should be allowed."""
        query = "MaTcH (n) ReTuRn n"
        assert is_read_only_query(query) is True

    def test_create_in_string_literal_single_quotes(self) -> None:
        """CREATE keyword in string literal (single quotes) should not trigger."""
        query = "MATCH (n) WHERE n.text = 'CREATE TABLE' RETURN n"
        assert is_read_only_query(query) is True

    def test_create_in_string_literal_double_quotes(self) -> None:
        """CREATE keyword in string literal (double quotes) should not trigger."""
        query = 'MATCH (n) WHERE n.text = "CREATE INDEX" RETURN n'
        assert is_read_only_query(query) is True

    def test_delete_in_string_literal(self) -> None:
        """DELETE keyword in string literal should not trigger."""
        query = "MATCH (n) WHERE n.action = 'DELETE' RETURN n"
        assert is_read_only_query(query) is True

    def test_create_in_single_line_comment(self) -> None:
        """CREATE in single-line comment should not trigger."""
        query = """
        // This comment mentions CREATE
        MATCH (n) RETURN n
        """
        assert is_read_only_query(query) is True

    def test_delete_in_multi_line_comment(self) -> None:
        """DELETE in multi-line comment should not trigger."""
        query = """
        /* This comment mentions DELETE
           and spans multiple lines */
        MATCH (n) RETURN n
        """
        assert is_read_only_query(query) is True

    def test_multi_line_query_with_create(self) -> None:
        """Multi-line query with CREATE should be blocked."""
        query = """
        MATCH (a)
        CREATE (b:Person)
        RETURN a, b
        """
        assert is_read_only_query(query) is False

    def test_multi_line_allowed_query(self) -> None:
        """Multi-line allowed query should pass."""
        query = """
        MATCH (n:Person)
        WHERE n.age > 30
        RETURN n.name, n.age
        ORDER BY n.age DESC
        LIMIT 10
        """
        assert is_read_only_query(query) is True

    def test_multiple_write_keywords(self) -> None:
        """Query with multiple write keywords should be blocked."""
        query = "MATCH (n) CREATE (m) SET n.name = 'Test' DELETE m"
        assert is_read_only_query(query) is False

    def test_set_in_property_name_allowed(self) -> None:
        """SET as part of a property name should not trigger."""
        query = "MATCH (n) WHERE n.dataset = 'test' RETURN n"
        assert is_read_only_query(query) is True

    def test_query_with_comment_and_string(self) -> None:
        """Complex query with both comments and strings should work correctly."""
        query = """
        // Find nodes with specific text
        MATCH (n)
        WHERE n.description = 'Contains DELETE keyword'
        // CREATE should not trigger in comments
        RETURN n
        """
        assert is_read_only_query(query) is True

    def test_detach_delete_mixed_case(self) -> None:
        """DETACH DELETE in mixed case should be blocked."""
        query = "MATCH (n) DeTaCh DeLeTe n"
        assert is_read_only_query(query) is False
