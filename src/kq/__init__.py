"""
kq - KQL CLI for Azure Data Explorer.

A command-line tool for querying Azure Data Explorer (Kusto) clusters
with support for saved queries, multiple clusters, and rich output.

Usage:
    kq auth login               # Authenticate
    kq list                     # List saved queries
    kq run <query> [params...]  # Run a saved query
    kq "PLC | take 5"           # Run raw KQL
"""

__version__ = "0.1.0"
