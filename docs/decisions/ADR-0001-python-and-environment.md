# ADR-0001: Python Version and Environment Management

## Status
Accepted
Date: 2026-08-05

## Context
We need a reproducible Python environment that enforces strict dependency locking.
The preferred Python target is 3.14.

## Decision
* We will use **Python 3.14** (specifically 3.14.6 resolved locally).
* We will use **uv** for dependency management and locking.
* We will use **staged compatibility gates** rather than full-stack ahead-of-time compatibility checks.

## Evidence
* `uv lock` successfully resolved and downloaded CPython 3.14.6.
* All Phase 0 dependencies (ruff, mypy, pytest, pre-commit, pip-audit, detect-secrets) successfully resolved and installed under Python 3.14.
* The failed prior broad-stack probe in Phase 1A proved that testing the entire Phase 1 stack prematurely introduces blocking issues (e.g., `tokenizers` build failure on Python 3.14) unrelated to current implementation needs.
* Staged compatibility replaced all-stack compatibility to isolate dependencies, prevent unrelated failures, and enforce strict "just-in-time" verification (Phase 1B).
* Exact executed evidence: `uv run --group phase1b-compat python scripts/verify_phase1b_compatibility.py` succeeded for Pydantic, Pydantic Settings, and HTTPX.

## Consequences
* Fast and reproducible environment builds.
* Contributors must have `uv` installed.
* `uv.lock` is tracked in git.

## Revisit Conditions
* If a future phase (e.g., Phase 1C or 1D) requires Python 3.13 due to lack of Python 3.14 wheel support, we will evaluate fallback to Python 3.13 and modify the project version accordingly.
