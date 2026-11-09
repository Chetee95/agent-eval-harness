"""Where hidden tests run.

* ``LocalSandbox`` runs commands as a subprocess. Fast, used in CI and self-tests.
* ``DockerSandbox`` runs them in a throwaway container with no network and capped
  CPU/memory, so agent-written code can't touch the host or phone home.

``{python}`` in a test command is replaced with the right interpreter for the sandbox.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

MAX_LOG_CHARS = 200_000


@dataclass
class ExecResult:
    returncode: int
    stdout: str
    stderr: str
    duration_s: float
    timed_out: bool

    @property
    def combined_log(self) -> str:
        return _truncate(self.stdout + ("\n--- stderr ---\n" + self.stderr if self.stderr else ""))


def _truncate(text: str) -> str:
    if len(text) <= MAX_LOG_CHARS:
        return text
    half = MAX_LOG_CHARS // 2
    return text[:half] + "\n...[truncated]...\n" + text[-half:]


def _to_text(data: bytes | str | None) -> str:
    if data is None:
        return ""
    return data.decode("utf-8", "replace") if isinstance(data, bytes) else data


def run_subprocess(
    argv: list[str] | str,
    cwd: Path,
    timeout_s: int,
    env: dict[str, str] | None = None,
    shell: bool = False,
) -> ExecResult:
    start = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env={**os.environ, **(env or {})},
        )
        return ExecResult(proc.returncode, proc.stdout, proc.stderr, time.monotonic() - start, False)
    except subprocess.TimeoutExpired as exc:
        return ExecResult(-1, _to_text(exc.stdout), _to_text(exc.stderr), time.monotonic() - start, True)


class LocalSandbox:
    name = "local"

    def run(self, command: str, workdir: Path, timeout_s: int) -> ExecResult:
        command = command.replace("{python}", sys.executable)
        return run_subprocess(command, cwd=workdir, timeout_s=timeout_s, shell=True)


class DockerSandbox:
    name = "docker"

    def __init__(self, image: str = "evalh-sandbox:latest", memory: str = "1g", cpus: str = "1.0"):
        self.image = image
        self.memory = memory
        self.cpus = cpus

    def build_argv(self, command: str, workdir: Path, container_name: str) -> list[str]:
        argv = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "none",
            "--memory", self.memory,
            "--cpus", self.cpus,
            "--pids-limit", "256",
            "-v", f"{Path(workdir).resolve()}:/work",
            "-w", "/work",
        ]
        if hasattr(os, "getuid"):  # keep files writable by the host user
            argv += ["--user", f"{os.getuid()}:{os.getgid()}"]
        return argv + [self.image, "sh", "-c", command]

    def run(self, command: str, workdir: Path, timeout_s: int) -> ExecResult:
        command = command.replace("{python}", "python")
        container_name = f"evalh-{uuid.uuid4().hex[:12]}"
        result = run_subprocess(self.build_argv(command, workdir, container_name), cwd=workdir, timeout_s=timeout_s)
        if result.timed_out:  # the client timed out; make sure the container dies too
            subprocess.run(["docker", "kill", container_name], capture_output=True)
        return result


def get_sandbox(name: str) -> LocalSandbox | DockerSandbox:
    if name == "local":
        return LocalSandbox()
    if name == "docker":
        return DockerSandbox()
    raise ValueError(f"unknown sandbox {name!r} (expected 'local' or 'docker')")
