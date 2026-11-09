"""The record written for every (task, agent) run. One JSON file per run."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class RunResult:
    task_id: str
    agent: str
    sandbox: str
    started_at: str
    # "passed" | "failed" | "test_timeout" | "error"
    status: str = "error"
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_errored: int = 0
    tests_skipped: int = 0
    files_changed: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    agent_exit_code: int = 0
    agent_timed_out: bool = False
    agent_duration_s: float = 0.0
    test_duration_s: float = 0.0
    failure_category: str = "unclassified"
    error: str = ""

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    @property
    def test_pass_fraction(self) -> float:
        return self.tests_passed / self.tests_total if self.tests_total else 0.0

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_file(cls, path: Path) -> "RunResult":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})
