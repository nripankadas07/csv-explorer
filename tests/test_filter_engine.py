"""Tests for the filter engine module."""

import pytest

from csv_explorer.filter_engine import (
    sort_rows,
    filter_rows,
    filter_rows_regex,
    search_all_columns,
    apply_numeric_filter,
)


@pytest.fixture
def sample_rows() -> list[list[str]]:
    return [
        ["Alice", "30", "New York", "95.5"],
        ["Bob", "25", "London", "87.3"],
        ["Charlie", "35", "Paris", "92.1"],
        ["Diana", "28", "Tokyo", "88.9"],
    ]


class TestSortRows:
    def test_sort_by_text_column(self, sample_rows: list) -> None:
        sorted_rows = sort_rows(sample_rows, 0)
        assert sorted_rows[0][0] == "Alice"
        assert sorted_rows[3][0] == "Diana"

    def test_sort_descending(self, sample_rows: list) -> None:
        sorted_rows = sort_rows(sample_rows, 0, reverse=True)
        assert sorted_rows[0][0] == "Diana"

    def test_sort_numeric(self, sample_rows: list) -> None:
        sorted_rows = sort_rows(sample_rows, 1, numeric=True)
        assert sorted_rows[0][1] == "25"
        assert sorted_rows[-1][1] == "35"

    def test_sort_with_missing_values(self) -> None:
        rows = [["Alice", "30"], ["Bob"], ["Charlie", "25"]]
        sorted_rows = sort_rows(rows, 1, numeric=True)
        assert sorted_rows[-1] == ["Bob"]  # Missing sorts last

    def test_sort_numeric_descending(self, sample_rows: list) -> None:
        sorted_rows = sort_rows(sample_rows, 3, numeric=True, reverse=True)
        assert sorted_rows[0][3] == "95.5"


class TestFilterRows:
    def test_filter_exact_match(self, sample_rows: list) -> None:
        result = filter_rows(sample_rows, 0, "Alice")
        assert len(result) == 1
        assert result[0][0] == "Alice"

    def test_filter_substring(self, sample_rows: list) -> None:
        result = filter_rows(sample_rows, 2, "New")
        assert len(result) == 1
        assert result[0][2] == "New York"

    def test_filter_case_insensitive(self, sample_rows: list) -> None:
        result = filter_rows(sample_rows, 0, "alice", case_sensitive=False)
        assert len(result) == 1

    def test_filter_case_sensitive(self, sample_rows: list) -> None:
        result = filter_rows(sample_rows, 0, "alice", case_sensitive=True)
        assert len(result) == 0

    def test_filter_empty_pattern(self, sample_rows: list) -> None:
        result = filter_rows(sample_rows, 0, "")
        assert len(result) == 4

    def test_filter_no_match(self, sample_rows: list) -> None:
        result = filter_rows(sample_rows, 0, "Zara")
        assert len(result) == 0


class TestFilterRowsRegex:
    def test_regex_basic(self, sample_rows: list) -> None:
        result = filter_rows_regex(sample_rows, 0, r"^[AB]")
        assert len(result) == 2

    def test_regex_invalid(self, sample_rows: list) -> None:
        with pytest.raises(ValueError, match="Invalid regex"):
            filter_rows_regex(sample_rows, 0, r"[invalid")

    def test_regex_case_insensitive(self, sample_rows: list) -> None:
        result = filter_rows_regex(sample_rows, 0, r"^alice", case_sensitive=False)
        assert len(result) == 1


class TestSearchAllColumns:
    def test_search_found(self, sample_rows: list) -> None:
        result = search_all_columns(sample_rows, "York")
        assert len(result) == 1

    def test_search_multiple_matches(self, sample_rows: list) -> None:
        # "o" appears in Bob, London, Tokyo
        result = search_all_columns(sample_rows, "o")
        assert len(result) >= 2

    def test_search_empty_query(self, sample_rows: list) -> None:
        result = search_all_columns(sample_rows, "")
        assert len(result) == 4

    def test_search_no_results(self, sample_rows: list) -> None:
        result = search_all_columns(sample_rows, "zzzzz")
        assert len(result) == 0


class TestApplyNumericFilter:
    def test_greater_than(self, sample_rows: list) -> None:
        result = apply_numeric_filter(sample_rows, 1, ">", 28)
        assert len(result) == 2  # 30, 35

    def test_less_than(self, sample_rows: list) -> None:
        result = apply_numeric_filter(sample_rows, 1, "<", 30)
        assert len(result) == 2  # 25, 28

    def test_equals(self, sample_rows: list) -> None:
        result = apply_numeric_filter(sample_rows, 1, "==", 30)
        assert len(result) == 1

    def test_greater_equal(self, sample_rows: list) -> None:
        result = apply_numeric_filter(sample_rows, 1, ">=", 30)
        assert len(result) == 2

    def test_not_equal(self, sample_rows: list) -> None:
        result = apply_numeric_filter(sample_rows, 1, "!=", 30)
        assert len(result) == 3

    def test_invalid_operator(self, sample_rows: list) -> None:
        with pytest.raises(ValueError, match="Unknown operator"):
            apply_numeric_filter(sample_rows, 1, "~", 30)
