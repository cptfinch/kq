"""Configuration management with XDG support."""

import os
from pathlib import Path
from typing import Optional

import yaml


def get_config_dir() -> Path:
    """Get config directory following XDG spec."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        base = Path(xdg_config)
    else:
        base = Path.home() / ".config"
    return base / "kq"


def get_data_dir() -> Path:
    """Get data directory following XDG spec."""
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        base = Path(xdg_data)
    else:
        base = Path.home() / ".local" / "share"
    return base / "kq"


# Paths
CONFIG_DIR = get_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.yaml"
USER_QUERIES_DIR = CONFIG_DIR / "queries"
BUNDLED_QUERIES_DIR = Path(__file__).parent / "queries"


class Config:
    """Configuration manager."""

    def __init__(self):
        self._config = {}
        self._load()

    def _load(self):
        """Load config from file."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                self._config = yaml.safe_load(f) or {}

    def _save(self):
        """Save config to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False)

    @property
    def default_cluster(self) -> Optional[str]:
        """Get default cluster URL."""
        name = self._config.get("default_cluster")
        if name and name in self.clusters:
            return self.clusters[name].get("url")
        return name  # Might be a direct URL

    @property
    def default_database(self) -> Optional[str]:
        """Get default database."""
        name = self._config.get("default_cluster")
        if name and name in self.clusters:
            return self.clusters[name].get("database")
        return self._config.get("default_database")

    @property
    def clusters(self) -> dict:
        """Get configured clusters."""
        return self._config.get("clusters", {})

    def get_cluster(self, name: str) -> Optional[dict]:
        """Get cluster config by name."""
        return self.clusters.get(name)

    @property
    def query_paths(self) -> list[Path]:
        """Get query search paths in priority order."""
        paths = []

        # 1. Project-local queries
        local_kq = Path.cwd() / ".kq"
        if local_kq.exists():
            paths.append(local_kq)

        # 2. User queries (XDG config)
        if USER_QUERIES_DIR.exists():
            paths.append(USER_QUERIES_DIR)

        # 3. Custom paths from config
        for p in self._config.get("query_paths", []):
            path = Path(p).expanduser()
            if path.exists():
                paths.append(path)

        # 4. Bundled queries (lowest priority)
        if BUNDLED_QUERIES_DIR.exists():
            paths.append(BUNDLED_QUERIES_DIR)

        return paths

    def set(self, key: str, value: str):
        """Set a config value."""
        self._config[key] = value
        self._save()

    def add_cluster(self, name: str, url: str, database: str = None):
        """Add a cluster configuration."""
        if "clusters" not in self._config:
            self._config["clusters"] = {}
        self._config["clusters"][name] = {"url": url}
        if database:
            self._config["clusters"][name]["database"] = database
        self._save()

    def show(self) -> str:
        """Return config as YAML string."""
        return yaml.dump(self._config, default_flow_style=False)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
