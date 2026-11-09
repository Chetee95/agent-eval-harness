from app.config import load_config


def describe(overrides=None):
    cfg = load_config(overrides)
    return f"db={cfg['database_url']} debug={cfg['debug']}"
