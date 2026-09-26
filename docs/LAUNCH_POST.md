# Launch post drafts

Three formats below: a blog/dev.to post, short Reddit/forum variants, and a
one-line social post. Pick per venue; they say the same thing at different
lengths.

---

## A) Blog / dev.to — "I built jq for Kusto"

**Title:** I built `jq` for Kusto — a tiny CLI for querying Azure Data Explorer

I run a lot of KQL against Azure Data Explorer, and I kept hitting the same
friction: the web UI is great for exploring but terrible for automation, and
`az kusto` isn't built for quick, pipeable, everyday queries. I wanted the thing
`jq` is for JSON — small, fast, lives in the terminal, composes with pipes.

So I built **`kq`**.

```bash
pip install kql-cli   # the command is `kq`

kq config set default_cluster https://mycluster.kusto.windows.net
kq config set default_database mydb
kq auth login

kq "MyTable | take 5"
kq "MyTable | summarize count() by bin(Timestamp, 1h)" -f json | jq .
```

The part I actually care about most is **saved, git-versioned queries**. You
write parameterized queries in YAML and run them by name:

```yaml
# ~/.config/kq/queries/ops.yaml
queries:
  - name: errors
    description: Recent errors for a service
    parameters:
      - {name: service, required: true}
      - {name: hours, default: "24"}
    query: |
      Traces
      | where Timestamp > ago({hours}h)
      | where Service == '{service}'
      | where Level == 'Error'
      | order by Timestamp desc
```

```bash
kq run ops.errors checkout 6
```

Queries resolve from a project-local `./.kq/`, then your user queries, then
bundled examples — so a repo can ship its own query library, and your personal
queries never get clobbered by an update.

A few other things it does:

- **Auth that just works** — service principal → Azure CLI → cached device code,
  with ~90-day silent refresh (handy on WSL/headless).
- **`table` / `json` / `csv`** output — the JSON pipes straight into `jq`.
- **Query safety levels** (`safe` / `caution` / `dangerous`) to keep expensive
  full-table scans honest.
- **Plays nicely with LLM coding agents** — clean, deterministic output.

It's MIT-licensed, tested on Python 3.9–3.13, and on PyPI as `kql-cli`.

Repo: https://github.com/cptfinch/kq

If you work with Kusto/ADX, I'd love feedback — especially on what saved-query
patterns you'd want built in.

---

## B) Reddit / Hacker News "Show" variants

**Title options**
- Show: kq — jq for Kusto/KQL (query Azure Data Explorer from the CLI)
- I built a small CLI for querying Azure Data Explorer (like jq, but for KQL)

**Body (r/AZURE, r/dataengineering, r/kusto):**

I kept wanting a `jq`-style tool for KQL — something small and pipeable for
querying Azure Data Explorer from the terminal, instead of the web UI or
`az kusto`. So I made `kq`.

- `kq "MyTable | take 5"` for raw KQL, `-f json|csv` for output
- Saved, parameterized queries in YAML that you can git-version per project
- Auth chain: service principal → Azure CLI → cached device code (~90-day refresh)
- Query safety levels to flag expensive scans

`pip install kql-cli` (the command is `kq`). MIT, tested on 3.9–3.13.

https://github.com/cptfinch/kq

Curious what saved-query patterns people would find useful — and how others are
scripting against ADX today.

---

## C) One-liner (X / Mastodon / LinkedIn)

`kq` — jq, but for Kusto/KQL. Query Azure Data Explorer from the terminal: raw
KQL, git-versioned saved queries, json/csv output, sane auth.

`pip install kql-cli` · MIT · https://github.com/cptfinch/kq

---

## Posting notes

- Best-fit communities: r/AZURE, r/dataengineering, r/kusto, the Azure Data
  Explorer community, and Show HN.
- Post *after* PyPI is live so `pip install kql-cli` works from the first click.
- The README demo GIF (`docs/demo.gif`) is worth embedding in the dev.to post
  too — a moving demo roughly doubles conversion.
- Lead with the `jq` analogy every time; it's the fastest way people "get it."
