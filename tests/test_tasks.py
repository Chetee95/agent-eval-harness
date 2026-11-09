"""Every task must be solvable (reference passes) and meaningful (noop fails)."""

import pytest

from evalh.agents import NoopAgent, ReferenceAgent
from evalh.runner import run_task
from evalh.sandbox import LocalSandbox
from evalh.task import load_tasks

from .conftest import ROOT

TASKS = load_tasks(ROOT / "tasks")


@pytest.mark.parametrize("task", TASKS, ids=[t.id for t in TASKS])
def test_reference_solution_passes(task, tmp_path):
    result = run_task(task, ReferenceAgent(), LocalSandbox(), tmp_path)
    assert result.status == "passed", result.error or (tmp_path / "runs").glob("*/test.log")
    assert result.tests_total > 0
    assert result.files_changed > 0


@pytest.mark.parametrize("task", TASKS, ids=[t.id for t in TASKS])
def test_unchanged_repo_fails(task, tmp_path):
    result = run_task(task, NoopAgent(), LocalSandbox(), tmp_path)
    assert result.status == "failed"
    assert result.files_changed == 0
    assert result.tests_passed < result.tests_total


def test_at_least_three_tasks():
    assert len(TASKS) >= 3
