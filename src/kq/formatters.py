"""Output formatters for query results.

These functions are deliberately free of any Azure SDK imports so they can be
unit-tested against a plain object. They expect a result table that quacks like
``azure.kusto.data``'s ``KustoResultTable``:

- ``.columns`` — a sequence of objects exposing ``.column_name``
- iteration — yields rows, each an iterable of cell values
- ``.rows_count`` — total number of rows
- ``.to_dict()`` — returns ``{"data": [ {column: value}, ... ]}``
"""

import json

MAX_TABLE_ROWS = 50
MAX_CELL_WIDTH = 30


def format_table(results, max_rows: int = MAX_TABLE_ROWS) -> str:
    """Format results as a readable, fixed-width table."""
    if not results:
        return "No results."

    headers = [col.column_name for col in results.columns]
    lines = [" | ".join(headers)]
    lines.append("-" * min(len(lines[0]), 100))

    for i, row in enumerate(results):
        if i >= max_rows:
            lines.append(f"... ({results.rows_count - max_rows} more rows)")
            break
        values = []
        for v in row:
            s = str(v) if v is not None else ""
            values.append(s[:MAX_CELL_WIDTH] + "..." if len(s) > MAX_CELL_WIDTH else s)
        lines.append(" | ".join(values))

    return "\n".join(lines)


def format_json(results) -> str:
    """Format results as a JSON array."""
    if not results:
        return "[]"

    data = results.to_dict().get("data", [])

    def serialize(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return str(obj)

    return json.dumps(data, indent=2, default=serialize)


def format_csv(results) -> str:
    """Format results as CSV (RFC 4180-style quoting)."""
    if not results:
        return ""

    lines = []
    headers = [col.column_name for col in results.columns]
    lines.append(",".join(f'"{h}"' for h in headers))

    for row in results:
        values = []
        for v in row:
            s = str(v) if v is not None else ""
            if '"' in s:
                s = s.replace('"', '""')
            if "," in s or '"' in s or "\n" in s:
                s = f'"{s}"'
            values.append(s)
        lines.append(",".join(values))

    return "\n".join(lines)
