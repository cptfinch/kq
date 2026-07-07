"""Tests for the Azure-free output formatters."""

import json
from datetime import datetime

from kq.formatters import format_csv, format_json, format_table
from tests.conftest import FakeResultTable


def test_table_has_header_and_rows(simple_table):
    out = format_table(simple_table)
    lines = out.splitlines()
    assert lines[0] == "Name | Count"
    assert lines[1].startswith("---")
    assert "alpha | 1" in out
    assert "beta | 2" in out


def test_table_none_results():
    assert format_table(None) == "No results."


def test_table_truncates_wide_cells():
    wide = "x" * 100
    table = FakeResultTable(["Col"], [[wide]])
    out = format_table(table)
    assert "..." in out
    # 30 chars kept + ellipsis, never the full 100
    assert wide not in out


def test_table_row_limit_notes_remainder():
    rows = [[i] for i in range(60)]
    table = FakeResultTable(["N"], rows)
    out = format_table(table, max_rows=50)
    assert "... (10 more rows)" in out


def test_json_roundtrips(simple_table):
    out = format_json(simple_table)
    data = json.loads(out)
    assert data == [{"Name": "alpha", "Count": 1}, {"Name": "beta", "Count": 2}]


def test_json_serializes_datetimes():
    table = FakeResultTable(["ts"], [[datetime(2026, 1, 2, 3, 4, 5)]])
    data = json.loads(format_json(table))
    assert data[0]["ts"] == "2026-01-02T03:04:05"


def test_json_empty():
    assert format_json(None) == "[]"


def test_csv_quotes_headers(simple_table):
    out = format_csv(simple_table)
    assert out.splitlines()[0] == '"Name","Count"'


def test_csv_escapes_commas_and_quotes():
    table = FakeResultTable(["v"], [["a,b"], ['say "hi"'], ["plain"]])
    lines = format_csv(table).splitlines()
    assert lines[1] == '"a,b"'          # comma forces quoting
    assert lines[2] == '"say ""hi"""'   # embedded quotes doubled
    assert lines[3] == "plain"          # nothing special, left bare


def test_csv_quotes_embedded_newline():
    # A newline inside a field must stay wrapped in quotes (a single CSV
    # record that happens to span two physical lines).
    table = FakeResultTable(["v"], [["line1\nline2"]])
    out = format_csv(table)
    assert '"line1\nline2"' in out


def test_csv_escapes_quotes_in_headers():
    # A quote in a column name must be doubled, not emitted raw.
    table = FakeResultTable(['My "Special" Column'], [["x"]])
    assert format_csv(table).splitlines()[0] == '"My ""Special"" Column"'


def test_csv_quotes_bare_carriage_return():
    # A lone \r (no \n) must still force quoting per RFC 4180.
    table = FakeResultTable(["v"], [["a\rb"]])
    out = format_csv(table)
    assert '"a\rb"' in out


def test_csv_no_trailing_newline(simple_table):
    assert not format_csv(simple_table).endswith("\n")


def test_csv_empty():
    assert format_csv(None) == ""
