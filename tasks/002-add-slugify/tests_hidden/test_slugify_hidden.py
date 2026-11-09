import pytest

import textutils
from textutils import slugify


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello World", "hello-world"),
        ("  Hello,   World!  ", "hello-world"),
        ("Crème Brûlée", "creme-brulee"),
        ("Python 3.12 Release Notes", "python-3-12-release-notes"),
        ("---already--slugged---", "already-slugged"),
        ("日本語 title", "title"),
        ("", ""),
    ],
)
def test_basic_slugs(text, expected):
    assert slugify(text) == expected


def test_max_length_strips_trailing_hyphen():
    assert slugify("hello world foo", max_length=6) == "hello"


def test_max_length_longer_than_slug():
    assert slugify("short", max_length=50) == "short"


def test_invalid_max_length():
    with pytest.raises(ValueError):
        slugify("x", max_length=0)


def test_existing_functions_untouched():
    assert textutils.truncate("abcdefghij", 6) == "abc..."
    assert textutils.word_count("one two  three") == 3
