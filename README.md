# kq

KQL CLI - Query Azure Data Explorer from the command line.

Like `jq` for JSON, but for Kusto/KQL.

## Installation

```bash
pip install kq
```

Or from source:

```bash
git clone https://github.com/cptfinch/kq.git
cd kq
pip install -e .
```

## Quick Start

```bash
# Configure your cluster
kq config set default_cluster https://mycluster.westeurope.kusto.windows.net
kq config set default_database mydb

# Authenticate
kq auth login

# Run queries
kq "MyTable | take 5"                    # Raw KQL
kq list                                   # List saved queries
kq run examples.sample MyTable 10         # Run saved query
```

## Configuration

Config is stored in `~/.config/kq/config.yaml`:

```yaml
default_cluster: https://mycluster.westeurope.kusto.windows.net
default_database: mydb

clusters:
  prod:
    url: https://prod.westeurope.kusto.windows.net
    database: proddb
  dev:
    url: https://dev.westeurope.kusto.windows.net
    database: devdb
```

Configure via CLI:

```bash
kq config show                              # Show current config
kq config set default_cluster <url>         # Set default cluster
kq config set default_database <db>         # Set default database
kq config add-cluster prod <url> --database proddb  # Add named cluster
```

## Commands

| Command | Description |
|---------|-------------|
| `kq auth login` | Authenticate to ADX |
| `kq auth status` | Check authentication status |
| `kq config show` | Show configuration |
| `kq config set <key> <value>` | Set config value |
| `kq list [category]` | List saved queries |
| `kq show <query>` | Show query details |
| `kq run <query> [params...]` | Run a saved query |
| `kq "<kql>"` | Run raw KQL |

## Saved Queries

Queries are loaded from (in priority order):

1. `./.kq/` - Project-local queries
2. `~/.config/kq/queries/` - User queries
3. Bundled examples

### Query Format

Create YAML files in `~/.config/kq/queries/`:

```yaml
# ~/.config/kq/queries/myqueries.yaml
name: myqueries
description: My custom queries

queries:
  - name: recent
    description: Get recent records
    safety: safe
    parameters:
      - name: table
        description: Table name
        required: true
      - name: hours
        description: Hours to look back
        default: "24"
    query: |
      {table}
      | where Timestamp > ago({hours}h)
      | order by Timestamp desc
      | take 100
    example: "MyTable 24"
```

Then run:

```bash
kq list                        # Shows myqueries.recent
kq show myqueries.recent       # Show details
kq run myqueries.recent Events # Run with parameters
```

## Output Formats

```bash
kq "MyTable | take 5" -f table    # Default - human readable
kq "MyTable | take 5" -f json     # JSON array
kq "MyTable | take 5" -f csv      # CSV
```

## Authentication

Supports (in priority order):

1. **Service Principal** - Set `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
2. **Azure CLI** - Run `az login` first
3. **Device Code** - Interactive browser login (tokens cached ~90 days)

## Query Safety

Queries have a `safety` level:

- `safe` - Queries with proper time/scope filtering
- `caution` - May scan significant data, use carefully
- `dangerous` - Can scan entire tables, requires explicit filtering

Always filter by time first:

```kql
// Good - filters first, cheap
MyTable | where Timestamp > ago(1d) | where Category == 'Error'

// Bad - scans everything, expensive
MyTable | where Category == 'Error'
```

## Why kq?

- **LLM-native** - Works seamlessly with Claude Code, Copilot, etc.
- **Portable** - Same queries work across clusters
- **Versionable** - Git-controlled query libraries
- **Unix-friendly** - Pipes, scripts, automation
- **Personal queries** - User queries never overwritten by updates

## License

MIT
