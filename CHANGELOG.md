# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-11-27

### Removed
- Support for Python 3.9, which reached end-of-life in October 2025. `kq` now
  requires Python 3.10 or newer. Users still on 3.9 can keep using 1.0.0:
  `pip` selects it automatically on that interpreter.

### Changed
- CI tests Python 3.10–3.13. All jobs run on the current `ubuntu-latest`
  runners, which no longer provide Python 3.9.
- Type hints use the Python 3.10 `X | None` syntax.
- The README (also the PyPI project page) adds a demo recording, a "Why kq?"
  section comparing it with the ADX web UI and `az kusto`, and a
  `uv tool install kql-cli` option.

### Fixed
- README links to the demo GIF and the license are absolute, so they work on
  PyPI as well as on GitHub.

## [1.0.0] - 2026-07-07

First public release on PyPI.

### Added
- Query Azure Data Explorer (Kusto) from the command line: raw KQL, saved
  parameterized queries, and bundled examples.
- Multi-cluster configuration with XDG-compliant config in
  `~/.config/kq/config.yaml`.
- Layered query resolution: project-local `.kq/`, user `~/.config/kq/queries/`,
  then bundled examples.
- Authentication chain: service principal → Azure CLI → cached device code
  (with ~90-day silent refresh).
- Output formats: `table`, `json`, `csv`.
- Query safety levels (`safe` / `caution` / `dangerous`).
- Test suite, `ruff` linting, GitHub Actions CI (Python 3.9–3.13), and a
  Trusted-Publishing release workflow.

### Note
- The tool is distributed on PyPI as **`kql-cli`** (the command remains `kq`),
  because the `kq` name on PyPI is taken by an unrelated project.

[Unreleased]: https://github.com/cptfinch/kq/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/cptfinch/kq/releases/tag/v1.1.0
[1.0.0]: https://github.com/cptfinch/kq/releases/tag/v1.0.0
