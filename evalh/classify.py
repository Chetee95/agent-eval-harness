"""Failure-mode classification. ★ YOUR PART ★

This is where your real-world evaluation experience shows. Recruiters reading this repo
should see a thoughtful taxonomy, not just a pass/fail number.

Implement ``classify`` so that ``tests/test_classify.py`` passes, then remove the
``xfail`` marker in that file. Rules, checked in this order (first match wins):

1. The run passed                                   -> NONE
2. The agent timed out                              -> AGENT_TIMEOUT
3. The agent exited non-zero AND changed no files   -> AGENT_CRASH
4. The agent changed no files                       -> NO_CHANGES
5. The hidden tests timed out                       -> TEST_TIMEOUT
6. The test log shows the code could not even be imported
   (look for "SyntaxError", "IndentationError", "ImportError",
   "ModuleNotFoundError", or "error during collection")
                                                    -> BROKEN_CODE
7. Some hidden tests passed, some did not           -> PARTIAL_FIX
8. Anything else (changes made, zero tests passed)  -> WRONG_FIX

Stretch ideas once the basics work (good material for your write-up):
* OVER_EDITING: passed or failed, but touched far more lines than the reference solution.
* TEST_TAMPERING: the agent edited or deleted the repo's own tests.
* An LLM-as-judge pass over ``agent_log`` to tag "hallucinated API", "lost context", "gave up".
"""

from __future__ import annotations

from enum import Enum

from .result import RunResult


class FailureCategory(str, Enum):
    NONE = "none"
    AGENT_TIMEOUT = "agent_timeout"
    AGENT_CRASH = "agent_crash"
    NO_CHANGES = "no_changes"
    TEST_TIMEOUT = "test_timeout"
    BROKEN_CODE = "broken_code"
    PARTIAL_FIX = "partial_fix"
    WRONG_FIX = "wrong_fix"
    UNCLASSIFIED = "unclassified"


def classify(result: RunResult, agent_log: str, test_log: str) -> FailureCategory:
    """Return the failure category for one run. See the module docstring for the rules."""
    # TODO(chete): implement the rules above. Until then every run is UNCLASSIFIED.
    return FailureCategory.UNCLASSIFIED
