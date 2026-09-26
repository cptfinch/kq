# kq v1.0.0 — first public release

Paste this into the GitHub Release body when tagging `v1.0.0`.

---

`kq` is a KQL CLI for Azure Data Explorer (Kusto). Like `jq` for JSON, but for
KQL — run raw queries, keep a git-versioned library of parameterized queries,
and pipe results straight into your shell.

## Install

```bash
pip install kql-cli
```

The command is `kq`. (The PyPI package is `kql-cli` because `kq` was already
taken on PyPI by an unrelated project.)

## Quick start

```bash
kq config set default_cluster https://mycluster.westeurope.kusto.windows.net
kq config set default_database mydb
kq auth login

kq "MyTable | take 5"                 # raw KQL
kq "MyTable | take 5" -f json         # or -f csv
kq list                               # saved queries
kq run examples.sample MyTable 10     # run a saved query
```

## Highlights

- **Raw KQL and saved queries** — run KQL directly, or curate reusable,
  parameterized queries in YAML and run them by name.
- **Git-versionable query libraries** — queries resolve from `./.kq/` (project),
  `~/.config/kq/queries/` (user), then bundled examples. Your queries are never
  overwritten by updates.
- **Multi-cluster config** — named clusters, XDG-compliant config in
  `~/.config/kq/config.yaml`.
- **Flexible auth** — service principal → Azure CLI → cached device code, with
  ~90-day silent token refresh (great for WSL/headless).
- **Output formats** — `table`, `json`, `csv`.
- **Query safety levels** — mark queries `safe` / `caution` / `dangerous` to
  keep expensive full-table scans honest.
- **LLM-native & Unix-friendly** — clean, pipeable output that works well with
  Claude Code, Copilot, scripts, and automation.

## Quality

- Test suite + `ruff` linting.
- GitHub Actions CI across Python 3.9–3.13.
- Published via PyPI Trusted Publishing (OIDC — no stored tokens).

**Full changelog:** see [CHANGELOG.md](../CHANGELOG.md).
