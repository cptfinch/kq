"""Query registry - manage saved/curated queries."""

from pathlib import Path
from typing import Optional

import yaml

from .config import get_config


class Query:
    """A saved query with metadata."""

    def __init__(self, category: str, name: str, data: dict, source: Path = None):
        self.category = category
        self.name = name
        self.full_name = f"{category}.{name}"
        self.description = data.get("description", "")
        self.query_template = data.get("query", "")
        self.parameters = data.get("parameters", [])
        self.safety = data.get("safety", "safe")  # safe, caution, dangerous
        self.example = data.get("example", "")
        self.source = source  # Which file this came from

    def render(self, **kwargs) -> str:
        """Render query with parameters."""
        query = self.query_template
        for param in self.parameters:
            name = param["name"]
            value = kwargs.get(name, param.get("default"))
            if value is None and param.get("required", False):
                raise ValueError(f"Missing required parameter: {name}")
            if value is not None:
                query = query.replace(f"{{{name}}}", str(value))
        return query.strip()

    def __repr__(self):
        return f"Query({self.full_name})"


class Registry:
    """Query registry with multi-source loading."""

    def __init__(self):
        self.queries: dict[str, Query] = {}
        self.categories: dict[str, dict] = {}
        self._load_all()

    def _load_yaml(self, path: Path):
        """Load queries from a YAML file."""
        if not path.exists():
            return

        with open(path) as f:
            data = yaml.safe_load(f)

        if not data:
            return

        category = data.get("name", path.stem)
        self.categories[category] = {
            "description": data.get("description", ""),
            "file": str(path),
        }

        for q in data.get("queries", []):
            query = Query(category, q["name"], q, source=path)
            # Don't overwrite if already loaded (priority order)
            if query.full_name not in self.queries:
                self.queries[query.full_name] = query

    def _load_all(self):
        """Load queries from all configured paths."""
        config = get_config()
        for path in config.query_paths:
            if path.is_dir():
                for yaml_file in path.glob("*.yaml"):
                    self._load_yaml(yaml_file)
                for yaml_file in path.glob("*.yml"):
                    self._load_yaml(yaml_file)

    def get(self, name: str) -> Optional[Query]:
        """Get a query by full name (category.name)."""
        return self.queries.get(name)

    def search(self, pattern: str) -> list[Query]:
        """Search queries by name or description."""
        pattern = pattern.lower()
        results = []
        for query in self.queries.values():
            if (pattern in query.full_name.lower() or
                pattern in query.description.lower()):
                results.append(query)
        return results

    def list_all(self) -> list[Query]:
        """List all queries."""
        return sorted(self.queries.values(), key=lambda q: q.full_name)

    def list_category(self, category: str) -> list[Query]:
        """List queries in a category."""
        return [q for q in self.queries.values() if q.category == category]


# Global registry instance
_registry: Optional[Registry] = None


def get_registry() -> Registry:
    """Get the global registry instance."""
    global _registry
    if _registry is None:
        _registry = Registry()
    return _registry
