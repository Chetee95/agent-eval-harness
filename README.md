# agent-eval-harness

![CI](https://github.com/Chetee95/agent-eval-harness/actions/workflows/ci.yml/badge.svg)

**Reproducible, sandboxed benchmarking for AI coding agents.**
Give any CLI coding agent (Claude Code, Aider, Codex CLI, your own) a set of real repository tasks,
score its changes against hidden tests in an isolated container, and get a report that explains
*how* it failed, not just *whether* it failed.

```
$ evalh run --agent shell --name my-agent --cmd "my-agent --prompt-file {prompt_file}" --sandbox docker
Running 3 task(s) with agent 'my-agent' in 'docker' sandbox
[PASS] 001-fix-pagination           my-agent       tests 9/9    none
[FAIL] 002-add-slugify              my-agent       tests 8/11   partial_fix
[PASS] 003-rename-config-key        my-agent       tests 6/6    none

Solved 2/3. Report: results/report.md
```

## Why

Leaderboard numbers hide the things that matter when you put an agent on a real codebase: did it
break something else, did it touch 300 lines to fix 2, did it give up, did it even produce code
that imports? This harness records all of that for every run, so you can compare agents (or
versions of the same agent) on *your* kind of work.

## How it works

```
task/repo ──copy──▶ workspace ──git baseline──▶ agent edits ──▶ diff stats + patch
                                                                     │
                     tests_hidden ──copied in only now──▶ sandbox (no network, CPU/mem caps)
                                                                     │
                                          JUnit XML ──▶ score ──▶ failure classifier ──▶ report.md
```

1. Each task's starting repo is copied to a fresh workspace and committed as a git baseline.
2. The agent edits the workspace. It never sees the hidden tests.
3. The harness records files and lines changed and saves the full patch.
4. Hidden tests are copied in and run in the sandbox (`local` subprocess, or `docker` with
   `--network none`, memory, CPU and PID limits).
5. Results are classified into failure modes and written to `results/runs/<task>__<agent>/`
   (`result.json`, `agent.log`, `test.log`, `changes.patch`), plus a summary `results/report.md`.

## Quick start

```bash
pip install -e ".[dev]"
pytest                                   # self-tests: every task is solvable and non-trivial

evalh run --agent reference              # known-good solutions: should solve 3/3
evalh run --agent noop                   # no changes: should solve 0/3
cat results/report.md
```

Run a real agent in the Docker sandbox:

```bash
docker build -t evalh-sandbox:latest -f docker/Dockerfile.sandbox .
evalh run --agent shell --name claude-code \
  --cmd 'claude -p "$(cat {prompt_file})" --permission-mode acceptEdits' \
  --sandbox docker
```

The prompt is available to the agent command as `{prompt_file}`, `$EVAL_PROMPT_FILE` and `$EVAL_PROMPT`.

## Writing a task

```
tasks/004-your-task/
  task.yaml        # id, title, prompt (+ optional tags, timeout_s, test_command)
  repo/            # starting code
  tests_hidden/    # tests the agent never sees (name files uniquely, e.g. test_<x>_hidden.py)
  solution/        # files overlaid on repo/ by the reference agent
```

`pytest` checks that every task passes with its reference solution **and** fails with no changes,
so a broken or trivial task can't slip into the suite.

## Failure taxonomy

| Category | Meaning |
|---|---|
| `none` | Passed |
| `agent_timeout` | Agent ran out of time |
| `agent_crash` | Agent exited with an error and changed nothing |
| `no_changes` | Agent finished but edited nothing |
| `test_timeout` | Agent's code hung the test run |
| `broken_code` | Code no longer imports or parses |
| `partial_fix` | Some hidden tests pass |
| `wrong_fix` | Changes made, no hidden tests pass |

## Project layout

```
evalh/        task loading, agents, sandboxes, runner, classifier, report, CLI
tasks/        benchmark tasks
tests/        harness self-tests
docker/       sandbox image
```

## License

MIT
