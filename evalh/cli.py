"""Command line: ``evalh run`` and ``evalh report``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agents import get_agent
from .report import write_report
from .runner import run_suite
from .sandbox import get_sandbox
from .task import TaskError, load_tasks


def _cmd_run(args: argparse.Namespace) -> int:
    try:
        tasks = load_tasks(Path(args.tasks), args.task or None)
        agent = get_agent(args.agent, name=args.name, command=args.cmd)
        sandbox = get_sandbox(args.sandbox)
    except (TaskError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    def show(r):
        mark = "PASS" if r.passed else "FAIL"
        print(f"[{mark}] {r.task_id:<28} {r.agent:<14} tests {r.tests_passed}/{r.tests_total}  {r.failure_category}")

    print(f"Running {len(tasks)} task(s) with agent '{agent.name}' in '{sandbox.name}' sandbox")
    results = run_suite(tasks, [agent], sandbox, Path(args.out), on_result=show)
    report = write_report(Path(args.out))
    solved = sum(r.passed for r in results)
    print(f"\nSolved {solved}/{len(results)}. Report: {report}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    print(write_report(Path(args.out)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="evalh", description="Benchmark AI coding agents on sandboxed tasks.")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run an agent over the task suite")
    run.add_argument("--tasks", default="tasks", help="directory of task folders (default: tasks)")
    run.add_argument("--task", action="append", help="only run this task id (repeatable)")
    run.add_argument("--agent", default="reference", choices=["reference", "noop", "shell"])
    run.add_argument("--name", help="display name for a shell agent, e.g. claude-code")
    run.add_argument("--cmd", help="shell agent command; {prompt_file} is replaced with the prompt path")
    run.add_argument("--sandbox", default="local", choices=["local", "docker"])
    run.add_argument("--out", default="results", help="results directory (default: results)")
    run.set_defaults(func=_cmd_run)

    rep = sub.add_parser("report", help="regenerate report.md from a results directory")
    rep.add_argument("--out", default="results")
    rep.set_defaults(func=_cmd_report)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
