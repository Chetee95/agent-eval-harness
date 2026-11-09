from app.config import load_config


def connection_string(overrides=None):
    cfg = load_config(overrides)
    return cfg["database_url"]
