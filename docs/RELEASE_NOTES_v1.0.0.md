# kq v1.0.0 — first public release

Used as the body of the `v1.0.0` GitHub Release. The release workflow picks this
file up automatically for matching tags (see `.github/workflows/release.yml`).

---

`kq` is a small command-line tool for querying Azure Data Explorer (Kusto).

It exists because of a gap: the ADX web UI is lovely for exploring and useless
for automation, and `az kusto` manages clusters rather than querying them. There
was no obvious way to just *run a KQL query in a terminal and do something with
the answer*. So — `jq`, but for Kusto.

```bash
pip install kql-cli        # or: uv tool install kql-cli
```

The command is `kq`. The package is `kql-cli` because `kq` was already taken on
PyPI by an unrelated project.

## Getting started

```bash
kq config set default_cluster https://mycluster.westeurope.kusto.windows.net
kq config set default_database mydb
kq auth login

kq "MyTable | take 5"                  # raw KQL
kq "MyTable | take 5" -f json | jq .   # pipe it anywhere
```

## What's in it

**Saved queries are the good part.** Write parameterized queries in YAML and run
them by name:

```bash
kq run ops.errors checkout 6
```

They resolve from `./.kq/` (project), then `~/.config/kq/queries/` (yours), then
the bundled examples — so a repo can ship its own query library, your personal
queries never get clobbered by an update, and the whole thing lives in git
instead of someone's browser tabs.

**The rest:**

- Raw KQL or saved queries, with `table` / `json` / `csv` output.
- Multi-cluster config — run the same query against dev, staging or prod.
- Auth that gets out of the way: service principal → Azure CLI → cached device
  code, with ~90-day silent refresh (pleasant on WSL and headless boxes).
- Query safety levels (`safe` / `caution` / `dangerous`) to keep accidental
  full-table scans honest.
- Clean, deterministic output — handy for scripts and for coding agents.

## Housekeeping

MIT licensed. Tested on Python 3.9 through 3.13 in CI, linted with `ruff`, and
published to PyPI via Trusted Publishing (OIDC), so no tokens are stored
anywhere.

Full details in [CHANGELOG.md](https://github.com/cptfinch/kq/blob/main/CHANGELOG.md).

If you work with Kusto, I'd genuinely like to hear which saved-query patterns
you'd want built in — [open an issue](https://github.com/cptfinch/kq/issues).
