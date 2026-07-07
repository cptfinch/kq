"""Tests for config resolution and query-path precedence."""

from kq import config as config_mod
from kq.config import Config


def test_default_cluster_direct_url():
    c = Config()
    c._config = {"default_cluster": "https://x.kusto.windows.net"}
    assert c.default_cluster == "https://x.kusto.windows.net"


def test_default_cluster_named_lookup():
    c = Config()
    c._config = {
        "default_cluster": "prod",
        "clusters": {"prod": {"url": "https://prod.kusto.windows.net", "database": "pdb"}},
    }
    assert c.default_cluster == "https://prod.kusto.windows.net"
    assert c.default_database == "pdb"


def test_default_database_standalone():
    c = Config()
    c._config = {
        "default_cluster": "https://x.kusto.windows.net",
        "default_database": "mydb",
    }
    assert c.default_database == "mydb"


def test_add_cluster_mutates_config(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / "config.yaml")
    c = Config()
    c._config = {}
    c.add_cluster("dev", "https://dev.kusto.windows.net", database="devdb")
    assert c.clusters["dev"] == {
        "url": "https://dev.kusto.windows.net",
        "database": "devdb",
    }


def test_query_paths_priority_order(tmp_path, monkeypatch):
    local = tmp_path / "proj" / ".kq"
    user = tmp_path / "user_queries"
    bundled = tmp_path / "bundled"
    for d in (local, user, bundled):
        d.mkdir(parents=True)

    monkeypatch.chdir(tmp_path / "proj")
    monkeypatch.setattr(config_mod, "USER_QUERIES_DIR", user)
    monkeypatch.setattr(config_mod, "BUNDLED_QUERIES_DIR", bundled)

    c = Config()
    c._config = {}
    paths = c.query_paths
    # local project queries win, bundled examples are the fallback
    assert paths[0] == local
    assert paths[-1] == bundled
    assert user in paths
