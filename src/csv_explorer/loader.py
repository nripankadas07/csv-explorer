"""CSV file loading and parsing utilities."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any


def load_csv(path: str | Path) -> tuple[list[str], list[list[str]]]:
    """Load a CSV file and return (headers, rows).

    Args:
        path: Path to the CSV file.

    Returns:
        Tuple of (column_headers, row_data).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or has no headers.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")
    return parse_csv_text(text)


def parse_csv_text(text: str) -> tuple[list[str], list[list[str]]]:
    """Parse CSV text content and return (headers, rows).

    Args:
        text: CSV content as a string.

    Returns:
        Tuple of (column_headers, row_data).

    Raises:
        ValueError: If the text is empty or has no headers.
    """
    text = text.strip()
    if not text:
        raise ValueError("CSV content is empty")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        raise ValueError("CSV content is empty")

    headers = rows[0]
    if not any(h.strip() for h in headers):
        raise ValueError("CSV has no valid headers")

    data = rows[1:]
    return headers, data


def detect_column_types(headers: list[str], rows: list[list[str]]) -> dict[str, str]:
    """Detect column types (numeric, text) by sampling rows.

    Args:
        headers: Column header names.
        rows: Row data.

    Returns:
        Dict mapping column name to type string ("numeric" or "text").
    """
    types: dict[str, str] = {}
    sample = rows[:100]

    for i, header in enumerate(headers):
        numeric_count = 0
        total = 0
        for row in sample:
            if i < len(row) and row[i].strip():
                total += 1
                try:
                    float(row[i].strip().replace(",", ""))
                    numeric_count += 1
                except ValueError:
                    pass
        if total > 0 and numeric_count / total > 0.8:
            types[header] = "numeric"
        else:
            types[header] = "text"

    return types


def get_column_stats(
    headers: list[str], rows: list[list[str]], col_index: int
) -> dict[str, Any]:
    """Compute basic statistics for a column.

    Args:
        headers: Column header names.
        rows: Row data.
        col_index: Index of the column.

    Returns:
        Dict with statistics (count, unique, type, and numeric stats if applicable).
    """
    values = [row[col_index] for row in rows if col_index < len(row)]
    non_empty = [v for v in values if v.strip()]

    stats: dict[str, Any] = {
        "column": headers[col_index] if col_index < len(headers) else f"col_{col_index}",
        "count": len(values),
        "non_empty": len(non_empty),
        "unique": len(set(non_empty)),
    }

    # Try numeric stats
    numeric_vals: list[float] = []
    for v in non_empty:
        try:
            numeric_vals.append(float(v.strip().replace(",", "")))
        except ValueError:
            pass

    if len(numeric_vals) > len(non_empty) * 0.8 and numeric_vals:
        stats["type"] = "numeric"
        stats["min"] = min(numeric_vals)
        stats["max"] = max(numeric_vals)
        stats["mean"] = sum(numeric_vals) / len(numeric_vals)
    else:
        stats["type"] = "text"

    return stats
