"""Azure Data Explorer client."""

import io
from contextlib import redirect_stderr

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

from .auth import get_credential

# Re-exported for backward compatibility; formatters live in their own,
# Azure-free module so they can be unit-tested in isolation.
from .formatters import format_csv, format_json, format_table

__all__ = ["connect", "execute", "format_table", "format_json", "format_csv"]


def connect(cluster_url: str):
    """Connect to ADX cluster."""
    credential = get_credential(quiet=True)
    kcsb = KustoConnectionStringBuilder.with_azure_token_credential(cluster_url, credential)
    # Suppress noisy AzureCliCredential stderr from Kusto SDK
    with redirect_stderr(io.StringIO()):
        return KustoClient(kcsb)


def execute(query: str, cluster_url: str, database: str):
    """Execute a KQL query and return results."""
    client = connect(cluster_url)
    with redirect_stderr(io.StringIO()):
        response = client.execute(database, query)

    if not response.primary_results or not response.primary_results[0]:
        return None

    return response.primary_results[0]
