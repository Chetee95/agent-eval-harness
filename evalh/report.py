"""Turn a results directory into a Markdown report comparing agents."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .result import RunResult


def load_results(out_dir: Path) -> list[RunResult]:
    return [RunResult.from_file(p) for p in sorted(Path(out_dir).glob("runs/*/result.json"))]


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def render_markdown(results: list[RunResult]) -> str:
    if not results:
        return "# Evaluation report\n\nNo results found.\n"

    by_agent: dict[str, list[RunResult]] = defaultdict(list)
    for r in results:
        by_agent[r.agent].append(r)
    agents = sorted(by_agent)
    task_ids = sorted({r.task_id for r in results})

    lines = ["# Evaluation report", "", f"{len(task_ids)} task(s) · {len(agents)} agent(s)", ""]

    lines += [
        "## Summary",
        "",
        "| Agent | Tasks solved | Hidden tests passed | Avg agent time (s) | Avg lines changed |",
        "|---|---|---|---|---|",
    ]
    for a in agents:
        rs = by_agent[a]
        solved = sum(r.passed for r in rs)
        tests_passed = sum(r.tests_passed for r in rs)
        tests_total = sum(r.tests_total for r in rs)
        avg_time = sum(r.agent_duration_s for r in rs) / len(rs)
        avg_lines = sum(r.lines_added + r.lines_removed for r in rs) / len(rs)
        test_frac = _pct(tests_passed / tests_total) if tests_total else "n/a"
        lines.append(
            f"| {a} | {solved}/{len(rs)} ({_pct(solved / len(rs))}) | {test_frac} | {avg_time:.1f} | {avg_lines:.0f} |"
        )

    lines += ["", "## Per task", "", "| Task | " + " | ".join(agents) + " |", "|---|" + "---|" * len(agents)]
    lookup = {(r.task_id, r.agent): r for r in results}
    for t in task_ids:
        cells = []
        for a in agents:
            r = lookup.get((t, a))
            if r is None:
                cells.append("—")
            elif r.passed:
                cells.append(f"✅ {r.tests_passed}/{r.tests_total}")
            else:
                cells.append(f"❌ {r.tests_passed}/{r.tests_total} `{r.failure_category}`")
        lines.append(f"| {t} | " + " | ".join(cells) + " |")

    lines += ["", "## Failure modes", "", "| Agent | Category | Runs |", "|---|---|---|"]
    for a in agents:
        counts = Counter(r.failure_category for r in by_agent[a] if not r.passed)
        if not counts:
            lines.append(f"| {a} | (no failures) | 0 |")
        for cat, n in counts.most_common():
            lines.append(f"| {a} | {cat} | {n} |")

    errors = [r for r in results if r.error]
    if errors:
        lines += ["", "## Harness errors", ""]
        lines += [f"- `{r.task_id}` / `{r.agent}`: {r.error}" for r in errors]

    return "\n".join(lines) + "\n"


def write_report(out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    path = out_dir / "report.md"
    path.write_text(render_markdown(load_results(out_dir)), encoding="utf-8")
    return path
