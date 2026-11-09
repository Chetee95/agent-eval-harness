# Portfolio roadmap

Goal: three public projects plus a few write-ups that prove you can build, evaluate and run
production software, aimed at AI evaluation/infrastructure, backend/platform, and healthtech roles.

**Legend:** 🧑‍💻 = you write it (so you can explain every line in an interview) · 🤝 = we build it together · ✅ = done

Rule for every project: no client, employer or Mercor data, code or prompts. Public or synthetic only.

---

## Project 1: agent-eval-harness (this repo) · ~3 weeks

### Milestone 1: working skeleton ✅
- ✅ Runner, git-baseline diffing, local + Docker sandboxes, JUnit scoring
- ✅ Agent adapters: `shell` (any CLI agent), `reference`, `noop`
- ✅ Markdown report, CLI, 3 starter tasks, self-tests, CI

### Milestone 2: make it yours (week 1)
- 🧑‍💻 Implement `classify()` in `evalh/classify.py` until `tests/test_classify.py` passes, then remove its `xfail` marker
- 🧑‍💻 Write 7 more tasks (goal: 10). Mix: 3 bug fixes, 2 features from a spec, 2 multi-file refactors, at least 1 SQL task (SQLite) to show your database skills
- 🧑‍💻 Replace `OWNER` in the README badge with your GitHub username
- 🤝 Review your tasks together for leaks (prompt giving away the answer) and weak hidden tests

### Milestone 3: real agents, real numbers (week 2)
- 🤝 Add `--trials N` and report pass@1 / pass@k with spread, since one run of an LLM is not a measurement
- 🧑‍💻 Run 2–3 real agents (e.g. Claude Code, Aider, a small open model) over all 10 tasks
- 🤝 Add token/cost capture where the agent CLI reports it
- 🧑‍💻 Stretch: `OVER_EDITING` and `TEST_TAMPERING` categories (ideas are in `classify.py`)

### Milestone 4: polish (week 3)
- 🤝 HTML report or dashboard with per-task drill-down into patches and logs
- 🤝 Option to run the agent itself inside a container, not just the tests
- 🧑‍💻 README: add a demo GIF and your real results table
- 🧑‍💻 Write-up #1 (see below)

---

## Project 2: healthcare claims intake service · ~4 weeks

A service that ingests claim or medical-record documents, extracts structured fields with an LLM,
validates them, and stores them, built the way a regulated company would want it.

- **Data:** Synthea synthetic patients, public CMS sample files, generated claim PDFs
- **Stack:** ASP.NET Core (C#) *or* FastAPI (Python) · SQL Server or Postgres · Azure Container Apps
- **Must-haves:** audit log of every read/write, PHI redaction in logs, role-based access, idempotent job processing with retries, OpenAPI docs
- **AI piece:** LLM field extraction **plus an accuracy eval** of that extraction (reuse Project 1 ideas)
- **Infra:** Bicep or Terraform, GitHub Actions deploy, separate dev/prod config

Milestones:
1. 🤝 Data model, API skeleton, local Docker Compose
2. 🧑‍💻 Validation rules and SQL schema (your Noridian domain knowledge shows here)
3. 🤝 LLM extraction + eval set of ~50 labeled documents
4. 🤝 Azure deploy via IaC + CI/CD (backs up your Azure Administrator cert)

## Project 3: reliability case study (built on Project 2) · ~1–2 weeks

- 🧑‍💻 Load test with k6 or Locust; record p50/p95 latency
- 🧑‍💻 Find and tune a slow SQL query; include before/after execution plans and timings
- 🤝 OpenTelemetry traces + metrics, alerts on error rate and latency
- 🧑‍💻 Runbook and one written postmortem of a staged incident

## Write-ups (publish on a personal site, dev.to, or LinkedIn)

1. "How AI coding agents fail on real repos: lessons from building an eval harness" (after Project 1)
2. "Building a HIPAA-minded document pipeline with LLM extraction you can measure" (after Project 2)
3. "Tuning a slow SQL Server query: a worked example" (after Project 3)

## Profile checklist

- [ ] Pin the 3 repos on GitHub; profile README with a two-line summary
- [ ] Link GitHub + write-ups from resume header and LinkedIn Featured section
- [ ] Resume: add C#; add a start date to the Mercor role; add a "Projects" section with one line of impact per repo
