"""Tests for the query registry and parameter rendering."""

import pytest

from kq.registry import Query


def make_query(**data):
    return Query(category="cat", name="q", data=data)


def test_render_substitutes_named_params():
    q = make_query(
        query="{table} | take {count}",
        parameters=[{"name": "table"}, {"name": "count"}],
    )
    assert q.render(table="Events", count="5") == "Events | take 5"


def test_render_uses_defaults():
    q = make_query(
        query="{table} | take {count}",
        parameters=[
            {"name": "table"},
            {"name": "count", "default": "10"},
        ],
    )
    assert q.render(table="Events") == "Events | take 10"


def test_render_missing_required_raises():
    q = make_query(
        query="{table} | take 5",
        parameters=[{"name": "table", "required": True}],
    )
    with pytest.raises(ValueError, match="Missing required parameter: table"):
        q.render()


def test_render_strips_whitespace():
    q = make_query(query="\n  .show tables\n  ")
    assert q.render() == ".show tables"


def test_full_name_and_defaults():
    q = make_query(description="d", query="x")
    assert q.full_name == "cat.q"
    assert q.safety == "safe"  # default when unspecified
