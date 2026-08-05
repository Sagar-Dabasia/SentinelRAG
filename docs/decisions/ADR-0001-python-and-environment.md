# ADR-0001: Python Version and Environment Management

## Status
Accepted
Date: 2026-08-05

## Context
We need a reproducible Python environment that enforces strict dependency locking.
The preferred Python target is 3.14.

## Decision
* We will use **Python 3.14**. Python 3.14 is selected for Phase 0 and the exact Phase 1B dependency group. Full Phase 1 compatibility is not claimed.
* We will use **uv** for dependency management and locking.
* We will use **staged compatibility gates** rather than full-stack ahead-of-time compatibility checks. Staged compatibility is now mandatory.

## Evidence
* All Phase 0 dependencies (ruff, mypy, pytest, pre-commit, pip-audit, detect-secrets) successfully resolved and installed under Python 3.14.
* The failed broad-stack experiment proved that testing the entire Phase 1 stack prematurely introduces blocking issues unrelated to current implementation needs.
* Phase 1C, Phase 1D and Phase 1F require separate gates.
* Local Phase 1B evidence is pending independent remote audit.

## Consequences
* Fast and reproducible environment builds.
* Contributors must have `uv` installed.
* `uv.lock` is tracked in git.

## Revisit Conditions
* If a future phase (e.g., Phase 1C or 1D) requires Python 3.13 due to lack of Python 3.14 wheel support, we will evaluate fallback to Python 3.13 and modify the project version accordingly.
