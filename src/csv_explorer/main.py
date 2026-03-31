"""CLI entry point for csv-explorer."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from csv_explorer.loader import load_csv, get_column_stats, detect_column_types
from csv_explorer.filter_engine import (
    sort_rows,
    filter_rows,
    search_all_columns,
    apply_numeric_filter,
)
from csv_explorer.formatter import format_table, format_stats


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """csv-explorer: Terminal CSV viewer with sorting and filtering."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--sort", "-s", "sort_col", help="Column name or index to sort by")
@click.option("--desc", is_flag=True, help="Sort in descending order")
@click.option("--filter", "-f", "filter_expr", help="Filter: COLUMN=VALUE")
@click.option("--search", "-q", "search_query", help="Search across all columns")
@click.option("--head", "-n", type=int, default=0, help="Show first N rows (0=all)")
@click.option("--numeric-filter", help="Numeric filter: COLUMN>VALUE")
def view(
    file: str,
    sort_col: str | None,
    desc: bool,
    filter_expr: str | None,
    search_query: str | None,
    head: int,
    numeric_filter: str | None,
) -> None:
    """View a CSV file with optional sorting and filtering."""
    try:
        headers, rows = load_csv(file)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    col_types = detect_column_types(headers, rows)

    # Apply search
    if search_query:
        rows = search_all_columns(rows, search_query)

    # Apply column filter
    if filter_expr and "=" in filter_expr:
        col_name, _, value = filter_expr.partition("=")
        col_index = _resolve_column(headers, col_name.strip())
        if col_index is not None:
            rows = filter_rows(rows, col_index, value.strip())

    # Apply numeric filter
    if numeric_filter:
        rows = _apply_numeric_filter_expr(headers, rows, numeric_filter)

    # Apply sort
    if sort_col:
        col_index = _resolve_column(headers, sort_col)
        if col_index is not None:
            is_numeric = col_types.get(headers[col_index], "text") == "numeric"
            rows = sort_rows(rows, col_index, reverse=desc, numeric=is_numeric)

    # Apply head
    if head > 0:
        rows = rows[:head]

    click.echo(format_table(headers, rows))
    click.echo(f"\n{len(rows)} rows displayed")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--column", "-c", help="Show stats for a specific column")
def stats(file: str, column: str | None) -> None:
    """Show statistics for a CSV file."""
    try:
        headers, rows = load_csv(file)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if column:
        col_index = _resolve_column(headers, column)
        if col_index is None:
            click.echo(f"Error: Column '{column}' not found", err=True)
            sys.exit(1)
        col_stats = get_column_stats(headers, rows, col_index)
        click.echo(format_stats([col_stats]))
    else:
        all_stats = [get_column_stats(headers, rows, i) for i in range(len(headers))]
        click.echo(format_stats(all_stats))


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def columns(file: str) -> None:
    """List column names and detected types."""
    try:
        headers, rows = load_csv(file)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    col_types = detect_column_types(headers, rows)
    for i, header in enumerate(headers):
        click.echo(f"  {i}: {header} ({col_types.get(header, 'text')})")


def _resolve_column(headers: list[str], col_ref: str) -> int | None:
    """Resolve a column reference (name or index) to a column index."""
    # Try as index
    try:
        idx = int(col_ref)
        if 0 <= idx < len(headers):
            return idx
    except ValueError:
        pass

    # Try as name (case-insensitive)
    lower_ref = col_ref.lower()
    for i, h in enumerate(headers):
        if h.lower() == lower_ref:
            return i
    return None


def _apply_numeric_filter_expr(
    headers: list[str], rows: list[list[str]], expr: str
) -> list[list[str]]:
    """Parse and apply a numeric filter expression like 'price>100'."""
    import re

    match = re.match(r"(.+?)(>>|<=|!=|==|>|<)(.+)", expr)
    if not match:
        return rows

    col_name, op, value_str = match.groups()
    col_index = _resolve_column(headers, col_name.strip())
    if col_index is None:
        return rows

    try:
        threshold = float(value_str.strip())
    except ValueError:
        return rows

    return apply_numeric_filter(rows, col_index, op, threshold)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
