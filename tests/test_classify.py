"""Spec for evalh.classify.classify(). ★ YOUR PART ★

These are marked xfail until you implement classify(). When they all pass,
delete the `pytestmark` line below so CI enforces them from then on.
"""

import pytest

from evalh.classify import FailureCategory as C
from evalh.classify import classify
from evalh.result import RunResult

pytestmark = pytest.mark.xfail(reason="TODO(chete): implement classify()", strict=False)


def make(**kw) -> RunResult:
    base = dict(task_id="t", agent="a", sandbox="local", started_at="now",
                status="failed", tests_total=4, files_changed=1)
    base.update(kw)
    return RunResult(**base)


def test_passed():
    assert classify(make(status="passed", tests_passed=4), "", "") is C.NONE


def test_agent_timeout_beats_everything_else():
    assert classify(make(agent_timed_out=True, files_changed=0), "", "") is C.AGENT_TIMEOUT


def test_agent_crash():
    assert classify(make(agent_exit_code=1, files_changed=0), "Traceback...", "") is C.AGENT_CRASH


def test_no_changes():
    assert classify(make(files_changed=0), "I could not find the bug.", "") is C.NO_CHANGES


def test_test_timeout():
    assert classify(make(status="test_timeout"), "", "") is C.TEST_TIMEOUT


@pytest.mark.parametrize("log", [
    "E   SyntaxError: invalid syntax",
    "ModuleNotFoundError: No module named 'pager'",
    "ERROR collecting eval_hidden_tests/test_x.py\n!!! error during collection !!!",
])
def test_broken_code(log):
    assert classify(make(tests_passed=0), "", log) is C.BROKEN_CODE


def test_partial_fix():
    assert classify(make(tests_passed=2, tests_failed=2), "", "2 failed, 2 passed") is C.PARTIAL_FIX


def test_wrong_fix():
    assert classify(make(tests_passed=0, tests_failed=4), "", "4 failed") is C.WRONG_FIX
