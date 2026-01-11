"""kq CLI - Command line interface."""

import sys
import argparse

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from . import __version__
from . import auth
from . import client
from .config import get_config, CONFIG_FILE, USER_QUERIES_DIR
from .registry import get_registry


console = Console()


def get_cluster_and_db(args):
    """Get cluster URL and database from args or config."""
    config = get_config()

    cluster_url = getattr(args, 'cluster', None)
    database = getattr(args, 'database', None)

    if not cluster_url:
        cluster_url = config.default_cluster

    if not database:
        database = config.default_database

    return cluster_url, database


def cmd_auth(args):
    """Handle auth subcommands."""
    config = get_config()
    cluster_url = getattr(args, 'cluster', None) or config.default_cluster

    if args.auth_cmd == "login":
        if not cluster_url:
            print("No cluster configured. Use --cluster URL or run: kq config set default_cluster URL")
            return 1
        success = auth.login(cluster_url, device_code=True)
        return 0 if success else 1
    elif args.auth_cmd == "status":
        success = auth.status(cluster_url)
        return 0 if success else 1
    else:
        print(f"Unknown auth command: {args.auth_cmd}")
        return 1


def cmd_config(args):
    """Handle config subcommands."""
    config = get_config()

    if args.config_cmd == "show":
        console.print(f"[dim]Config file:[/dim] {CONFIG_FILE}")
        console.print(f"[dim]User queries:[/dim] {USER_QUERIES_DIR}")
        console.print()
        if CONFIG_FILE.exists():
            console.print(config.show())
        else:
            console.print("[dim]No config file yet. Run:[/dim]")
            console.print("  kq config set default_cluster https://your-cluster.kusto.windows.net")
        return 0

    elif args.config_cmd == "set":
        if not args.key or not args.value:
            print("Usage: kq config set <key> <value>")
            return 1
        config.set(args.key, args.value)
        print(f"Set {args.key} = {args.value}")
        return 0

    elif args.config_cmd == "add-cluster":
        if not args.name or not args.url:
            print("Usage: kq config add-cluster <name> <url> [--database DB]")
            return 1
        config.add_cluster(args.name, args.url, args.database)
        print(f"Added cluster: {args.name}")
        return 0

    return 0


def cmd_list(args):
    """List available queries."""
    registry = get_registry()

    if args.category:
        queries = registry.list_category(args.category)
        if not queries:
            print(f"No queries in category: {args.category}")
            return 1
    else:
        queries = registry.list_all()

    if not queries:
        print("No queries available.")
        print(f"Add query YAML files to: {USER_QUERIES_DIR}")
        return 1

    # Group by category
    by_category = {}
    for q in queries:
        by_category.setdefault(q.category, []).append(q)

    for category, cat_queries in sorted(by_category.items()):
        table = Table(title=f"[bold]{category}[/bold]", show_header=True)
        table.add_column("Query", style="cyan")
        table.add_column("Description")
        table.add_column("Params", style="dim")

        for q in cat_queries:
            params = ", ".join(p["name"] for p in q.parameters) or "-"
            table.add_row(q.name, q.description[:50], params)

        console.print(table)
        console.print()

    return 0


def cmd_show(args):
    """Show details of a query."""
    registry = get_registry()
    query = registry.get(args.name)

    if not query:
        matches = registry.search(args.name)
        if matches:
            print(f"Query '{args.name}' not found. Did you mean:")
            for m in matches[:5]:
                print(f"  - {m.full_name}")
        else:
            print(f"Query not found: {args.name}")
        return 1

    console.print(Panel(f"[bold]{query.full_name}[/bold]", subtitle=query.safety))
    console.print(f"[dim]Description:[/dim] {query.description}")
    if query.source:
        console.print(f"[dim]Source:[/dim] {query.source}")
    console.print()

    if query.parameters:
        console.print("[dim]Parameters:[/dim]")
        for p in query.parameters:
            req = "[red]*[/red]" if p.get("required") else ""
            default = f" (default: {p.get('default')})" if "default" in p else ""
            console.print(f"  {req}{p['name']}: {p.get('description', '')}{default}")
        console.print()

    console.print("[dim]Query:[/dim]")
    console.print(Syntax(query.query_template, "sql", theme="monokai"))

    if query.example:
        console.print()
        console.print(f"[dim]Example:[/dim] kq run {query.full_name} {query.example}")

    return 0


def cmd_run(args):
    """Run a saved query."""
    registry = get_registry()
    query = registry.get(args.name)

    if not query:
        print(f"Query not found: {args.name}")
        print(f"Run 'kq list' to see available queries")
        return 1

    # Parse positional params
    params = {}
    for i, p in enumerate(query.parameters):
        if i < len(args.params):
            params[p["name"]] = args.params[i]

    # Parse --key=value params
    for kv in args.params:
        if "=" in kv:
            k, v = kv.split("=", 1)
            params[k.lstrip("-")] = v

    try:
        rendered = query.render(**params)
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Run 'kq show {args.name}' for parameter details")
        return 1

    if args.dry_run:
        console.print("[dim]Query (dry run):[/dim]")
        console.print(Syntax(rendered, "sql", theme="monokai"))
        return 0

    cluster_url, database = get_cluster_and_db(args)

    if not cluster_url:
        print("No cluster configured. Use --cluster URL or run: kq config set default_cluster URL")
        return 1

    if not database:
        print("No database configured. Use --database DB or configure in cluster settings")
        return 1

    try:
        results = client.execute(rendered, cluster_url, database)

        if args.format == "table":
            print(client.format_table(results))
        elif args.format == "json":
            print(client.format_json(results))
        elif args.format == "csv":
            print(client.format_csv(results))

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_query(args):
    """Run raw KQL query."""
    cluster_url, database = get_cluster_and_db(args)

    if not cluster_url:
        print("No cluster configured. Use --cluster URL or run: kq config set default_cluster URL")
        return 1

    if not database:
        print("No database configured. Use --database DB or configure in cluster settings")
        return 1

    try:
        results = client.execute(args.query, cluster_url, database)

        if args.format == "table":
            print(client.format_table(results))
        elif args.format == "json":
            print(client.format_json(results))
        elif args.format == "csv":
            print(client.format_csv(results))

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point."""
    # Handle raw query shortcut: kq "SELECT * FROM ..."
    # Must check before argparse
    known_commands = {"auth", "config", "list", "show", "run", "query", "--help", "-h", "--version"}
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith("-"):
        # Treat as raw query
        class Args:
            command = "query"
            query = sys.argv[1]
            format = "table"
            cluster = None
            database = None
        return cmd_query(Args())

    parser = argparse.ArgumentParser(
        prog="kq",
        description="KQL CLI - Query Azure Data Explorer from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kq config set default_cluster https://mycluster.kusto.windows.net
  kq config set default_database mydb
  kq auth login                     # Authenticate (first time)
  kq list                           # List saved queries
  kq show myqueries.recent          # Show query details
  kq run myqueries.recent 24        # Run with parameters
  kq "MyTable | take 5"             # Raw KQL

Query files:
  Add YAML files to ~/.config/kq/queries/
  Or use project-local .kq/ directory
        """
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # auth
    auth_parser = subparsers.add_parser("auth", help="Authentication")
    auth_parser.add_argument("auth_cmd", choices=["login", "status"], help="Auth command")
    auth_parser.add_argument("--cluster", help="Cluster URL")

    # config
    config_parser = subparsers.add_parser("config", help="Configuration")
    config_sub = config_parser.add_subparsers(dest="config_cmd")

    config_sub.add_parser("show", help="Show configuration")

    set_parser = config_sub.add_parser("set", help="Set a config value")
    set_parser.add_argument("key", nargs="?", help="Config key")
    set_parser.add_argument("value", nargs="?", help="Config value")

    add_cluster_parser = config_sub.add_parser("add-cluster", help="Add a cluster")
    add_cluster_parser.add_argument("name", nargs="?", help="Cluster name")
    add_cluster_parser.add_argument("url", nargs="?", help="Cluster URL")
    add_cluster_parser.add_argument("--database", help="Default database")

    # list
    list_parser = subparsers.add_parser("list", help="List saved queries")
    list_parser.add_argument("category", nargs="?", help="Filter by category")

    # show
    show_parser = subparsers.add_parser("show", help="Show query details")
    show_parser.add_argument("name", help="Query name (e.g., myqueries.recent)")

    # run
    run_parser = subparsers.add_parser("run", help="Run a saved query")
    run_parser.add_argument("name", help="Query name")
    run_parser.add_argument("params", nargs="*", help="Parameters")
    run_parser.add_argument("-f", "--format", choices=["table", "json", "csv"], default="table")
    run_parser.add_argument("--dry-run", action="store_true", help="Show query without running")
    run_parser.add_argument("--cluster", help="Cluster URL")
    run_parser.add_argument("--database", help="Database name")

    # query (raw) - also handle as positional for convenience
    query_parser = subparsers.add_parser("query", help="Run raw KQL")
    query_parser.add_argument("query", help="KQL query string")
    query_parser.add_argument("-f", "--format", choices=["table", "json", "csv"], default="table")
    query_parser.add_argument("--cluster", help="Cluster URL")
    query_parser.add_argument("--database", "-d", help="Database name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "auth":
        return cmd_auth(args)
    elif args.command == "config":
        if not args.config_cmd:
            args.config_cmd = "show"
        return cmd_config(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "show":
        return cmd_show(args)
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "query":
        return cmd_query(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
