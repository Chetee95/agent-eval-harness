import warnings

DEFAULTS = {"database_url": "sqlite:///app.db", "debug": False}


def load_config(overrides=None):
    cfg = dict(DEFAULTS)
    if overrides:
        overrides = dict(overrides)
        if "db_url" in overrides:
            warnings.warn("'db_url' is deprecated; use 'database_url'", DeprecationWarning, stacklevel=2)
            legacy = overrides.pop("db_url")
            overrides.setdefault("database_url", legacy)
        cfg.update(overrides)
    return cfg
