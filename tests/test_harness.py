import sys

import pytest

from evalh.agents import ShellAgent
from evalh.cli import main
from evalh.report import load_results, render_markdown
from evalh.runner import parse_junit, run_task
from evalh.sandbox import DockerSandbox, LocalSandbox
from evalh.task import Task, TaskError, load_task, load_tasks


def test_shell_agent_gets_prompt_and_its_edits_are_scored(tasks_dir, tmp_path):
    task = load_task(tasks_dir / "001-fix-pagination")
    # A fake "agent" that proves it received the prompt, then applies a correct fix.
    script = (
        "import os, pathlib;"
        "assert 'pager.py' in pathlib.Path(os.environ['EVAL_PROMPT_FILE']).read_text();"
        "p = pathlib.Path('pager.py');"
        "s = p.read_text().replace('start = page * per_page', 'start = (page - 1) * per_page');"
        "s = s.replace('return total // per_page', 'return -(-total // per_page)');"
        "p.write_text(s)"
    )
    agent = ShellAgent("fake-agent", f'"{sys.executable}" -c "{script}"')
    result = run_task(task, agent, LocalSandbox(), tmp_path)
    assert result.agent_exit_code == 0
    assert result.status == "passed"
    assert result.files_changed == 1
    assert result.lines_added == 2 and result.lines_removed == 2
    patch = (tmp_path / "runs" / "001-fix-pagination__fake-agent" / "changes.patch").read_text()
    assert "(page - 1) * per_page" in patch


def test_agent_cannot_see_hidden_tests(tasks_dir, tmp_path):
    task = load_task(tasks_dir / "001-fix-pagination")
    agent = ShellAgent("peeker", f'"{sys.executable}" -c "import os,sys; sys.exit(int(os.path.exists(\'eval_hidden_tests\')))"')
    result = run_task(task, agent, LocalSandbox(), tmp_path)
    assert result.agent_exit_code == 0


def test_agent_timeout_is_recorded(tasks_dir, tmp_path):
    base = load_task(tasks_dir / "001-fix-pagination")
    task = Task(base.id, base.title, base.prompt, base.root, base.test_command, timeout_s=1)
    agent = ShellAgent("sleeper", f'"{sys.executable}" -c "import time; time.sleep(5)"')
    result = run_task(task, agent, LocalSandbox(), tmp_path)
    assert result.agent_timed_out


def test_parse_junit_handles_testsuites_root(tmp_path):
    xml = tmp_path / "r.xml"
    xml.write_text(
        '<testsuites><testsuite tests="5" failures="1" errors="1" skipped="1"/></testsuites>'
    )
    assert parse_junit(xml) == {"tests": 5, "failures": 1, "errors": 1, "skipped": 1}


def test_load_task_requires_fields(tmp_path):
    (tmp_path / "task.yaml").write_text("id: x\n")
    with pytest.raises(TaskError, match="title"):
        load_task(tmp_path)


def test_unknown_task_id(tasks_dir):
    with pytest.raises(TaskError, match="nope"):
        load_tasks(tasks_dir, ["nope"])


def test_docker_argv_is_locked_down(tmp_path):
    argv = DockerSandbox().build_argv("pytest", tmp_path, "c1")
    assert argv[argv.index("--network") + 1] == "none"
    assert "--memory" in argv and "--pids-limit" in argv


def test_cli_run_and_report(tasks_dir, tmp_path, capsys):
    out = tmp_path / "results"
    assert main(["run", "--tasks", str(tasks_dir), "--agent", "reference", "--out", str(out)]) == 0
    assert main(["run", "--tasks", str(tasks_dir), "--agent", "noop", "--out", str(out)]) == 0
    results = load_results(out)
    assert {r.agent for r in results} == {"reference", "noop"}
    report = (out / "report.md").read_text()
    assert "| reference | 3/3 (100%)" in report
    assert "| noop | 0/3 (0%)" in report
    assert render_markdown([]).startswith("# Evaluation report")
