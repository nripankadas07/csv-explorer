"""Output formatting utilities for terminal display."""

from __future__ import annotations

from typing import Any


def format_table(
    headers: list[str],
    rows: list[list[str]],
    max_col_width: int = 30,
) -> str:
    """Format headers and rows into an aligned text table.

    Args:
        headers: Column header names.
        rows: Row data.
        max_col_width: Maximum column width before truncation.

    Returns:
        Formatted table string.
    """
    if not headers:
        return "(empty table)"

    # Calculate column widths
    col_widths = [min(len(h), max_col_width) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = min(max(col_widths[i], len(val)), max_col_width)

    def truncate(val: str, width: int) -> str:
        if len(val) <= width:
            return val.ljust(width)
        return val[: width - 3] + "..."

    # Build header line
    header_line = " | ".join(truncate(h, col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)

    lines = [header_line, separator]

    for row in rows:
        cells = []
        for i in range(len(headers)):
            val = row[i] if i < len(row) else ""
            cells.append(truncate(val, col_widths[i]))
        lines.append(" | ".join(cells))

    return "\n".join(lines)


def format_stats(stats_list: list[dict[str, Any]]) -> str:
    """Format column statistics for display.

    Args:
        stats_list: List of stat dicts from get_column_stats.

    Returns:
        Formatted statistics string.
    """
    lines = []
    for stats in stats_list:
        lines.append(f"Column: {stats['column']}")
        lines.append(f"  Type:      {stats.get('type', 'unknown')}")
        lines.append(f"  Count:     {stats['count']}")
        lines.append(f"  Non-empty: {stats['non_empty']}")
        lines.append(f"  Unique:    {stats['unique']}")
        if stats.get("type") == "numeric":
            lines.append(f"  Min:       {stats['min']:.2f}")
            lines.append(f"  Max:       {stats['max']:.2f}")
            lines.append(f"  Mean:      {stats['mean']:.2f}")
        lines.append("")
    return "\n".join(lines)
