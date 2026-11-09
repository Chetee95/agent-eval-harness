"""Small text helpers used across the app."""

import re
import unicodedata


def truncate(text, limit, suffix="..."):
    """Shorten text to at most `limit` characters, adding `suffix` when cut."""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - len(suffix))] + suffix


def word_count(text):
    return len(text.split())


def slugify(text, max_length=None):
    """Turn a title into a lowercase, hyphen-separated ASCII slug."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if max_length is not None:
        if max_length < 1:
            raise ValueError("max_length must be >= 1")
        slug = slug[:max_length].rstrip("-")
    return slug
