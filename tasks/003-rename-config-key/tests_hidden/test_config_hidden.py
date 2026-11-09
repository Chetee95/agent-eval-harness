import pytest

from app import cli, db
from app.config import load_config


def test_default_uses_new_key():
    cfg = load_config()
    assert cfg["database_url"] == "sqlite:///app.db"
    assert "db_url" not in cfg


def test_new_key_override():
    assert db.connection_string({"database_url": "postgres://new"}) == "postgres://new"


def test_legacy_key_is_mapped_and_warns():
    with pytest.warns(DeprecationWarning):
        cfg = load_config({"db_url": "postgres://old"})
    assert cfg["database_url"] == "postgres://old"
    assert "db_url" not in cfg


def test_new_key_wins_when_both_given():
    with pytest.warns(DeprecationWarning):
        cfg = load_config({"db_url": "old", "database_url": "new"})
    assert cfg["database_url"] == "new"


def test_overrides_not_mutated():
    overrides = {"db_url": "old"}
    with pytest.warns(DeprecationWarning):
        load_config(overrides)
    assert overrides == {"db_url": "old"}


def test_cli_describe_uses_new_key():
    assert cli.describe({"database_url": "x"}) == "db=x debug=False"
