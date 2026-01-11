"""Azure Data Explorer client."""

import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

from .auth import get_credential


def connect(cluster_url: str):
    """Connect to ADX cluster."""
    credential = get_credential(quiet=True)
    kcsb = KustoConnectionStringBuilder.with_azure_token_credential(cluster_url, credential)
    return KustoClient(kcsb)


def execute(query: str, cluster_url: str, database: str):
    """Execute a KQL query and return results."""
    client = connect(cluster_url)
    response = client.execute(database, query)

    if not response.primary_results or not response.primary_results[0]:
        return None

    return response.primary_results[0]


def format_table(results, max_rows=50):
    """Format results as readable table."""
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
            values.append(s[:30] + "..." if len(s) > 30 else s)
        lines.append(" | ".join(values))

    return "\n".join(lines)


def format_json(results):
    """Format results as JSON array."""
    if not results:
        return "[]"

    data = results.to_dict().get("data", [])

    def serialize(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return str(obj)

    return json.dumps(data, indent=2, default=serialize)


def format_csv(results):
    """Format results as CSV."""
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
