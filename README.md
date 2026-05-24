# csv-explorer


A terminal CSV viewer with sorting, filtering, and search capabilities. Explore CSV files directly from your command line with powerful data manipulation features.

## Features

- **View CSV files** with aligned, formatted table output
- **Sort** by any column (text or numeric, ascending/descending)
- **Filter** rows by column value (substring or regex)
- **Search** across all columns simultaneously
- **Numeric filtering** with comparison operators (`>`, `<`, `>=`, `<=`, `==`, `!=`)
- **Column statistics** including type detection, min/max/mean for numeric columns
- **Auto-detects column types** (numeric vs text)

## Installation

```bash
pip install -e .
```

## Usage

### View a CSV File

```bash
csv-explorer view data.csv
```

### Sort by Column

```bash
# Sort by name (ascending)
csv-explorer view data.csv --sort name

# Sort by age (descending)
csv-explorer view data.csv --sort age --desc
```

### Filter Rows

```bash
# Filter where city contains "New"
csv-explorer view data.csv --filter "city=New"

# Numeric filter: age greater than 30
csv-explorer view data.csv --numeric-filter "age>30"
```

### Search Across All Columns

```bash
csv-explorer view data.csv --search "Alice"
```

### Show First N Rows

```bash
csv-explorer view data.csv --head 10
```

### Column Statistics

```bash
# Stats for all columns
csv-explorer stats data.csv

# Stats for a specific column
csv-explorer stats data.csv --column score
```

### List Columns

```bash
csv-explorer columns data.csv
```

## API Reference

### `csv_explorer.loader`

- `load_csv(path)` â Load a CSV file, returns `(headers, rows)`
- `parse_csv_text(text)` â Parse CSV text content
- `detect_column_types(headers, rows)` â Detect numeric vs text columns
- `get_column_stats(headers, rows, col_index)` â Compute column statistics

### `csv_explorer.filter_engine`

- `sort_rows(rows, col_index, reverse, numeric)` â Sort rows by column
- `filter_rows(rows, col_index, pattern, case_sensitive)` â Filter by substring
- `filter_rows_regex(rows, col_index, regex_pattern, case_sensitive)` â Filter by regex
- `search_all_columns(rows, query, case_sensitive)` â Search all columns
- `apply_numeric_filter(rows, col_index, operator, threshold)` â Numeric comparison filter

### `csv_explorer.formatter`

- `format_table(headers, rows, max_col_width)` â Format data as aligned text table
- `format_stats(stats_list)` â Format column statistics for display

## Architecture

```
src/csv_explorer/
âââ __init__.py          # Package metadata
âââ main.py              # CLI entry point (click commands)
âââ loader.py            # CSV loading, parsing, type detection
âââ filter_engine.py     # Sorting, filtering, search logic
âââ formatter.py         # Terminal output formatting
```

The project follows a clean separation of concerns: `loader.py` handles file I/O and parsing, `filter_engine.py` contains pure data transformation functions, and `formatter.py` manages output presentation. The `main.py` CLI layer orchestrates these components using Click.

## License

MIT License â Copyright 2024 Nripanka Das
