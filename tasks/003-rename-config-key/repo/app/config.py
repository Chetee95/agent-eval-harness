DEFAULTS = {"db_url": "sqlite:///app.db", "debug": False}


def load_config(overrides=None):
    cfg = dict(DEFAULTS)
    if overrides:
        cfg.update(overrides)
    return cfg
