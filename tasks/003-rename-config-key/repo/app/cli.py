from app.config import load_config


def describe(overrides=None):
    cfg = load_config(overrides)
    return f"db={cfg['db_url']} debug={cfg['debug']}"
