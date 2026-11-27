A small maintenance release.

## Python 3.10 or newer is now required

Python 3.9 reached end-of-life in October 2025, so `kq` 1.1.0 requires Python
3.10 or newer. Nothing changes if you're on 3.10–3.13.

Still on 3.9? You don't need to do anything: `pip install kql-cli` keeps
installing 1.0.0 on that interpreter, and it keeps working.

## Also in this release

- **A refreshed project page** — a demo recording, a "Why kq?" section comparing
  it with the ADX web UI and `az kusto`, and a `uv tool install kql-cli` option.
- **Working links on PyPI** — the README's demo and license links now resolve on
  PyPI as well as on GitHub.
- **Tidy-ups** — modern type hints, and CI on current GitHub runners for Python
  3.10–3.13.

## Upgrade

```bash
pip install -U kql-cli        # or: uv tool upgrade kql-cli
```

Full details in [CHANGELOG.md](https://github.com/cptfinch/kq/blob/main/CHANGELOG.md).
