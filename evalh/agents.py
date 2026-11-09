"""Agent adapters. An agent gets a task prompt and a working copy of the repo, and edits it.

* ``ShellAgent`` wraps any CLI coding agent (Claude Code, Aider, Codex CLI, your own script).
  The prompt is passed as ``$EVAL_PROMPT`` and as a file path in ``$EVAL_PROMPT_FILE``;
  ``{prompt_file}`` in the command template is replaced with that path.
* ``ReferenceAgent`` applies the task's known-good solution. It proves a task is solvable
  and that the harness scores a correct answer as passing.
* ``NoopAgent`` changes nothing. It proves the hidden tests actually fail on the starting repo.
"""

from __future__ import annotations

import shlex
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .sandbox import run_subprocess
from .task import Task


@dataclass
class AgentResult:
    exit_code: int
    duration_s: float
    timed_out: bool
    log: str


class Agent(Protocol):
    name: str

    def solve(self, task: Task, workdir: Path) -> AgentResult: ...


class NoopAgent:
    name = "noop"

    def solve(self, task: Task, workdir: Path) -> AgentResult:
        return AgentResult(exit_code=0, duration_s=0.0, timed_out=False, log="noop: made no changes\n")


class ReferenceAgent:
    name = "reference"

    def solve(self, task: Task, workdir: Path) -> AgentResult:
        start = time.monotonic()
        if not task.solution_dir.is_dir():
            return AgentResult(1, 0.0, False, f"reference: {task.id} has no solution/ directory\n")
        copied = []
        for src in sorted(task.solution_dir.rglob("*")):
            if src.is_file():
                rel = src.relative_to(task.solution_dir)
                dest = workdir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                copied.append(str(rel))
        log = "reference: applied " + ", ".join(copied) + "\n"
        return AgentResult(0, time.monotonic() - start, False, log)


class ShellAgent:
    def __init__(self, name: str, command: str):
        if not command:
            raise ValueError("ShellAgent needs a command, e.g. 'my-agent --prompt-file {prompt_file}'")
        self.name = name
        self.command = command

    def solve(self, task: Task, workdir: Path) -> AgentResult:
        # The prompt file lives outside the workspace so it never shows up in the diff.
        with tempfile.TemporaryDirectory(prefix="evalh-prompt-") as tmp:
            prompt_file = Path(tmp) / "PROMPT.md"
            prompt_file.write_text(task.prompt + "\n", encoding="utf-8")
            command = self.command.replace("{prompt_file}", shlex.quote(str(prompt_file)))
            res = run_subprocess(
                command,
                cwd=workdir,
                timeout_s=task.timeout_s,
                shell=True,
                env={"EVAL_PROMPT": task.prompt, "EVAL_PROMPT_FILE": str(prompt_file), "EVAL_TASK_ID": task.id},
            )
        return AgentResult(res.returncode, res.duration_s, res.timed_out, res.combined_log)


def get_agent(kind: str, name: str | None = None, command: str | None = None) -> Agent:
    if kind == "noop":
        return NoopAgent()
    if kind == "reference":
        return ReferenceAgent()
    if kind == "shell":
        return ShellAgent(name or "shell", command or "")
    raise ValueError(f"unknown agent kind {kind!r} (expected noop, reference or shell)")
