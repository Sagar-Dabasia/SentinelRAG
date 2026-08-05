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

## Evidence
* `uv lock` successfully resolved and downloaded CPython 3.14.6.
* All Phase 0 dependencies (ruff, mypy, pytest, pre-commit, pip-audit, detect-secrets) successfully resolved and installed under Python 3.14.
* Fallback to Python 3.13 was considered but rejected because 3.14 is fully supported by the current lockfile.

## Consequences
* Fast and reproducible environment builds.
* Contributors must have `uv` installed.
* `uv.lock` is tracked in git.
