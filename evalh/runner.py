"""Run one agent on one task, end to end.

1. Copy the task's repo into a fresh workspace and commit it as a git baseline.
2. Let the agent edit the workspace.
3. Record what changed (files, lines, full patch) against the baseline.
4. Copy in the hidden tests, run them in the sandbox, parse the JUnit XML.
5. Classify the outcome and write ``result.json`` plus logs.
"""

from __future__ import annotations

import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from .agents import Agent
from .classify import classify
from .result import RunResult
from .sandbox import ExecResult
from .task import HIDDEN_TESTS_DIRNAME, RESULTS_XML, Task


def _git(workdir: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=workdir, capture_output=True, text=True, check=True)
    return proc.stdout


def _init_baseline(workdir: Path) -> None:
    _git(workdir, "init", "-q")
    _git(workdir, "config", "user.email", "evalh@localhost")
    _git(workdir, "config", "user.name", "evalh")
    _git(workdir, "config", "commit.gpgsign", "false")
    _git(workdir, "add", "-A")
    _git(workdir, "commit", "-q", "--allow-empty", "-m", "baseline")


def _diff_stats(workdir: Path) -> tuple[int, int, int, str]:
    """Return (files_changed, lines_added, lines_removed, patch) relative to the baseline."""
    _git(workdir, "add", "-A")
    numstat = _git(workdir, "diff", "--cached", "--numstat")
    files = added = removed = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        files += 1
        if parts[0] != "-":  # "-" means a binary file
            added += int(parts[0])
            removed += int(parts[1])
    patch = _git(workdir, "diff", "--cached")
    return files, added, removed, patch


def parse_junit(xml_path: Path) -> dict[str, int]:
    root = ET.parse(xml_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in suites:
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    return totals


def run_task(task: Task, agent: Agent, sandbox, out_dir: Path) -> RunResult:
    run_dir = Path(out_dir) / "runs" / f"{task.id}__{agent.name}"
    workdir = run_dir / "workspace"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    shutil.copytree(task.repo_dir, workdir)

    result = RunResult(
        task_id=task.id,
        agent=agent.name,
        sandbox=sandbox.name,
        started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    agent_log = test_log = ""

    try:
        _init_baseline(workdir)

        agent_res = agent.solve(task, workdir)
        agent_log = agent_res.log
        result.agent_exit_code = agent_res.exit_code
        result.agent_timed_out = agent_res.timed_out
        result.agent_duration_s = round(agent_res.duration_s, 3)

        files, added, removed, patch = _diff_stats(workdir)
        result.files_changed, result.lines_added, result.lines_removed = files, added, removed
        (run_dir / "changes.patch").write_text(patch, encoding="utf-8")

        # Hidden tests go in only now, so the agent never sees them and they don't count as edits.
        hidden = workdir / HIDDEN_TESTS_DIRNAME
        if hidden.exists():
            shutil.rmtree(hidden)
        shutil.copytree(task.hidden_tests_dir, hidden)
        (workdir / RESULTS_XML).unlink(missing_ok=True)

        test_res: ExecResult = sandbox.run(task.test_command, workdir, task.timeout_s)
        test_log = test_res.combined_log
        result.test_duration_s = round(test_res.duration_s, 3)

        xml_path = workdir / RESULTS_XML
        if test_res.timed_out:
            result.status = "test_timeout"
        elif not xml_path.is_file():
            result.status = "error"
            result.error = f"test command produced no {RESULTS_XML} (exit {test_res.returncode})"
        else:
            totals = parse_junit(xml_path)
            result.tests_total = totals["tests"]
            result.tests_failed = totals["failures"]
            result.tests_errored = totals["errors"]
            result.tests_skipped = totals["skipped"]
            result.tests_passed = max(0, totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"])
            ok = test_res.returncode == 0 and result.tests_passed > 0 and not (result.tests_failed or result.tests_errored)
            result.status = "passed" if ok else "failed"
    except Exception as exc:  # a harness problem, not an agent problem: record it and move on
        result.status = "error"
        result.error = f"{type(exc).__name__}: {exc}"

    result.failure_category = classify(result, agent_log, test_log).value

    (run_dir / "agent.log").write_text(agent_log, encoding="utf-8")
    (run_dir / "test.log").write_text(test_log, encoding="utf-8")
    (run_dir / "result.json").write_text(result.to_json(), encoding="utf-8")
    return result


def run_suite(tasks: list[Task], agents: list[Agent], sandbox, out_dir: Path, on_result=None) -> list[RunResult]:
    results = []
    for agent in agents:
        for task in tasks:
            res = run_task(task, agent, sandbox, out_dir)
            results.append(res)
            if on_result:
                on_result(res)
    return results
