from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def tasks_dir() -> Path:
    return ROOT / "tasks"
