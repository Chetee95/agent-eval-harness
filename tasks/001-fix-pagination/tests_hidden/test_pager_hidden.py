import pytest

from pager import page_count, paginate

ITEMS = list(range(1, 26))  # 25 items


def test_first_page_starts_at_first_item():
    assert paginate(ITEMS, 1, 10) == list(range(1, 11))


def test_middle_page():
    assert paginate(ITEMS, 2, 10) == list(range(11, 21))


def test_last_partial_page():
    assert paginate(ITEMS, 3, 10) == [21, 22, 23, 24, 25]


def test_page_past_end_is_empty():
    assert paginate(ITEMS, 4, 10) == []


@pytest.mark.parametrize("total,per_page,expected", [(25, 10, 3), (20, 10, 2), (0, 10, 0), (1, 10, 1)])
def test_page_count(total, per_page, expected):
    assert page_count(total, per_page) == expected


def test_invalid_arguments_still_raise():
    with pytest.raises(ValueError):
        paginate(ITEMS, 0, 10)
    with pytest.raises(ValueError):
        page_count(10, 0)
