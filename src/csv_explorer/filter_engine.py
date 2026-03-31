"""Filtering and sorting engine for CSV data."""

from __future__ import annotations

import re
from typing import Callable


def sort_rows(
    rows: list[list[str]],
    col_index: int,
    reverse: bool = False,
    numeric: bool = False,
) -> list[list[str]]:
    """Sort rows by a specific column.

    Args:
        rows: List of row data.
        col_index: Column index to sort by.
        reverse: If True, sort in descending order.
        numeric: If True, sort numerically instead of lexicographically.

    Returns:
        New sorted list of rows.
    """

    def sort_key(row: list[str]) -> tuple:
        if col_index >= len(row):
            return (1, "")  # Missing values sort last
        val = row[col_index].strip()
        if not val:
            return (1, "")
        if numeric:
            try:
                return (0, float(val.replace(",", "")))
            except ValueError:
                return (1, val.lower())
        return (0, val.lower())

    return sorted(rows, key=sort_key, reverse=reverse)


def filter_rows(
    rows: list[list[str]],
    col_index: int,
    pattern: str,
    case_sensitive: bool = False,
) -> list[list[str]]:
    """Filter rows where a column matches a pattern (substring match).

    Args:
        rows: List of row data.
        col_index: Column index to filter on.
        pattern: Substring pattern to match.
        case_sensitive: If True, match is case-sensitive.

    Returns:
        Filtered list of rows.
    """
    if not pattern:
        return rows

    if not case_sensitive:
        pattern = pattern.lower()

    result = []
    for row in rows:
        if col_index >= len(row):
            continue
        val = row[col_index] if case_sensitive else row[col_index].lower()
        if pattern in val:
            result.append(row)
    return result


def filter_rows_regex(
    rows: list[list[str]],
    col_index: int,
    regex_pattern: str,
    case_sensitive: bool = False,
) -> list[list[str]]:
    """Filter rows where a column matches a regex pattern.

    Args:
        rows: List of row data.
        col_index: Column index to filter on.
        regex_pattern: Regular expression pattern.
        case_sensitive: If True, match is case-sensitive.

    Returns:
        Filtered list of rows.

    Raises:
        ValueError: If the regex pattern is invalid.
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled = re.compile(regex_pattern, flags)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}") from e

    result = []
    for row in rows:
        if col_index >= len(row):
            continue
        if compiled.search(row[col_index]):
            result.append(row)
    return result


def search_all_columns(
    rows: list[list[str]],
    query: str,
    case_sensitive: bool = False,
) -> list[list[str]]:
    """Search for a query string across all columns.

    Args:
        rows: List of row data.
        query: Search string.
        case_sensitive: If True, search is case-sensitive.

    Returns:
        Rows where any column contains the query.
    """
    if not query:
        return rows

    if not case_sensitive:
        query = query.lower()

    result = []
    for row in rows:
        for val in row:
            check = val if case_sensitive else val.lower()
            if query in check:
                result.append(row)
                break
    return result


def apply_numeric_filter(
    rows: list[list[str]],
    col_index: int,
    operator: str,
    threshold: float,
) -> list[list[str]]:
    """Filter rows based on numeric comparison.

    Args:
        rows: List of row data.
        col_index: Column index to filter on.
        operator: One of '>', '<', '>=', '<=', '==', '!='.
        threshold: Numeric threshold value.

    Returns:
        Filtered list of rows.

    Raises:
        ValueError: If operator is not recognized.
    """
    ops: dict[str, Callable[[float, float], bool]] = {
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }

    if operator not in ops:
        raise ValueError(f"Unknown operator: {operator}. Use one of {list(ops.keys())}")

    compare = ops[operator]
    result = []
    for row in rows:
        if col_index >= len(row):
            continue
        try:
            val = float(row[col_index].strip().replace(",", ""))
            if compare(val, threshold):
                result.append(row)
        except ValueError:
            continue
    return result
