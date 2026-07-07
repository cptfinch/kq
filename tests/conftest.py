"""Shared test fixtures."""

import pytest


class FakeColumn:
    def __init__(self, name):
        self.column_name = name


class FakeResultTable:
    """Minimal stand-in for azure.kusto.data's KustoResultTable.

    Supports the surface the formatters rely on: ``.columns``, iteration over
    rows, ``.rows_count`` and ``.to_dict()``.
    """

    def __init__(self, column_names, rows):
        self.columns = [FakeColumn(n) for n in column_names]
        self._rows = rows
        self.rows_count = len(rows)
        self._column_names = column_names

    def __iter__(self):
        return iter(self._rows)

    def __bool__(self):
        return True

    def to_dict(self):
        return {
            "data": [dict(zip(self._column_names, row)) for row in self._rows],
        }


@pytest.fixture
def simple_table():
    return FakeResultTable(["Name", "Count"], [["alpha", 1], ["beta", 2]])
