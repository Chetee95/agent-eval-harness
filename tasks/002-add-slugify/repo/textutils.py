"""Small text helpers used across the app."""


def truncate(text, limit, suffix="..."):
    """Shorten text to at most `limit` characters, adding `suffix` when cut."""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - len(suffix))] + suffix


def word_count(text):
    return len(text.split())
