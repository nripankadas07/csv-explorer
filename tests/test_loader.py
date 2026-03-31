"""Tests for the CSV loader module."""

import tempfile
from pathlib import Path

import pytest

from csv_explorer.loader import (
    load_csv,
    parse_csv_text,
    detect_column_types,
    get_column_stats,
)


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a sample CSV file for testing."""
    content = "name,age,city,score\nAlice,30,New York,95.5\nBob,25,London,87.3\nCharlie,35,Paris,92.1\nDiana,28,Tokyo,88.9\n"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(content)
    return csv_file


@pytest.fixture
def empty_csv(tmp_path: Path) -> Path:
    """Create an empty CSV file."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    return csv_file


class TestLoadCSV:
    def test_load_valid_csv(self, sample_csv: Path) -> None:
        headers, rows = load_csv(sample_csv)
        assert headers == ["name", "age", "city", "score"]
        assert len(rows) == 4
        assert rows[0] == ["Alice", "30", "New York", "95.5"]

    def test_load_nonexistent_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_csv("/nonexistent/file.csv")

    def test_load_empty_file(self, empty_csv: Path) -> None:
        with pytest.raises(ValueError, match="empty"):
            load_csv(empty_csv)


class TestParseCSVText:
    def test_parse_basic_csv(self) -> None:
        text = "a,b,c\n1,2,3\n4,5,6"
        headers, rows = parse_csv_text(text)
        assert headers == ["a", "b", "c"]
        assert len(rows) == 2

    def test_parse_empty_text(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            parse_csv_text("")

    def test_parse_whitespace_only(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            parse_csv_text("   \n  \n  ")

    def test_parse_headers_only(self) -> None:
        headers, rows = parse_csv_text("name,age,city")
        assert headers == ["name", "age", "city"]
        assert rows == []

    def test_parse_quoted_values(self) -> None:
        text = 'name,desc\n"Alice","Has a, comma"\n"Bob","Normal"'
        headers, rows = parse_csv_text(text)
        assert rows[0][1] == "Has a, comma"


class TestDetectColumnTypes:
    def test_detect_numeric(self) -> None:
        headers = ["name", "age", "score"]
        rows = [
            ["Alice", "30", "95.5"],
            ["Bob", "25", "87.3"],
            ["Charlie", "35", "92.1"],
        ]
        types = detect_column_types(headers, rows)
        assert types["name"] == "text"
        assert types["age"] == "numeric"
        assert types["score"] == "numeric"

    def test_detect_mixed_column(self) -> None:
        headers = ["value"]
        rows = [["10"], ["abc"], ["20"], ["def"], ["30"]]
        types = detect_column_types(headers, rows)
        assert types["value"] == "text"  # 60% numeric < 80% threshold


class TestGetColumnStats:
    def test_numeric_stats(self) -> None:
        headers = ["score"]
        rows = [["95.5"], ["87.3"], ["92.1"], ["88.9"]]
        stats = get_column_stats(headers, rows, 0)
        assert stats["type"] == "numeric"
        assert stats["min"] == 87.3
        assert stats["max"] == 95.5
        assert stats["count"] == 4

    def test_text_stats(self) -> None:
        headers = ["name"]
        rows = [["Alice"], ["Bob"], ["Alice"], ["Charlie"]]
        stats = get_column_stats(headers, rows, 0)
        assert stats["type"] == "text"
        assert stats["unique"] == 3
        assert stats["count"] == 4
