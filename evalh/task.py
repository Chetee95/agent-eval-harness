"""Task definitions: a starting repo, a prompt, hidden tests and a reference solution.

Layout of one task directory::

    tasks/001-fix-pagination/
        task.yaml        # id, title, prompt, optional test_command / timeout_s / tags
        repo/            # the code the agent starts from
        tests_hidden/    # tests the agent never sees; copied in only after it finishes
        solution/        # reference files, overlaid on repo/ by the `reference` agent
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

HIDDEN_TESTS_DIRNAME = "eval_hidden_tests"
RESULTS_XML = ".eval_results.xml"
DEFAULT_TEST_COMMAND = (
    f"{{python}} -m pytest {HIDDEN_TESTS_DIRNAME} -q -p no:cacheprovider "
    f"--junitxml={RESULTS_XML}"
)


class TaskError(ValueError):
    """Raised when a task directory is malformed."""


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    prompt: str
    root: Path
    test_command: str = DEFAULT_TEST_COMMAND
    timeout_s: int = 600
    tags: tuple[str, ...] = ()

    @property
    def repo_dir(self) -> Path:
        return self.root / "repo"

    @property
    def hidden_tests_dir(self) -> Path:
        return self.root / "tests_hidden"

    @property
    def solution_dir(self) -> Path:
        return self.root / "solution"


def load_task(path: Path) -> Task:
    path = Path(path)
    spec_file = path / "task.yaml"
    if not spec_file.is_file():
        raise TaskError(f"{path}: missing task.yaml")
    data = yaml.safe_load(spec_file.read_text(encoding="utf-8")) or {}

    missing = [k for k in ("id", "title", "prompt") if not data.get(k)]
    if missing:
        raise TaskError(f"{spec_file}: missing required field(s): {', '.join(missing)}")

    task = Task(
        id=str(data["id"]),
        title=str(data["title"]),
        prompt=str(data["prompt"]).strip(),
        root=path.resolve(),
        test_command=str(data.get("test_command", DEFAULT_TEST_COMMAND)),
        timeout_s=int(data.get("timeout_s", 600)),
        tags=tuple(data.get("tags", ()) or ()),
    )
    for required_dir in (task.repo_dir, task.hidden_tests_dir):
        if not required_dir.is_dir():
            raise TaskError(f"{path}: missing {required_dir.name}/ directory")
    return task


def load_tasks(tasks_dir: Path, ids: list[str] | None = None) -> list[Task]:
    tasks_dir = Path(tasks_dir)
    tasks = [load_task(p) for p in sorted(tasks_dir.iterdir()) if (p / "task.yaml").is_file()]
    if ids:
        wanted = set(ids)
        tasks = [t for t in tasks if t.id in wanted]
        unknown = wanted - {t.id for t in tasks}
        if unknown:
            raise TaskError(f"unknown task id(s): {', '.join(sorted(unknown))}")
    return tasks
