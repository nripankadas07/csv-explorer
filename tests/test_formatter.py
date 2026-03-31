"""Tests for the formatter module."""

from csv_explorer.formatter import format_table, format_stats


class TestFormatTable:
    def test_basic_table(self) -> None:
        headers = ["name", "age"]
        rows = [["Alice", "30"], ["Bob", "25"]]
        result = format_table(headers, rows)
        assert "name" in result
        assert "Alice" in result
        assert "Bob" in result

    def test_empty_table(self) -> None:
        result = format_table([], [])
        assert result == "(empty table)"

    def test_headers_only(self) -> None:
        result = format_table(["a", "b"], [])
        assert "a" in result
        assert "-" in result  # separator line present

    def test_truncation(self) -> None:
        headers = ["col"]
        rows = [["a" * 50]]
        result = format_table(headers, rows, max_col_width=10)
        assert "..." in result

    def test_missing_values(self) -> None:
        headers = ["a", "b", "c"]
        rows = [["1", "2"]]  # Missing third value
        result = format_table(headers, rows)
        assert "1" in result
        assert "2" in result


class TestFormatStats:
    def test_numeric_stats(self) -> None:
        stats = [
            {
                "column": "score",
                "type": "numeric",
                "count": 4,
                "non_empty": 4,
                "unique": 4,
                "min": 10.0,
                "max": 100.0,
                "mean": 55.0,
            }
        ]
        result = format_stats(stats)
        assert "score" in result
        assert "numeric" in result
        assert "10.00" in result
        assert "100.00" in result

    def test_text_stats(self) -> None:
        stats = [
            {
                "column": "name",
                "type": "text",
                "count": 3,
                "non_empty": 3,
                "unique": 2,
            }
        ]
        result = format_stats(stats)
        assert "name" in result
        assert "text" in result
