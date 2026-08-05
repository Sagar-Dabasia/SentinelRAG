# Contributing to SentinelRAG

We welcome contributions! However, please note that SentinelRAG is primarily a personal portfolio and research project, so PRs might be accepted selectively.

## Environment Setup
1. Ensure you have Python 3.14 (or fallback version) and `uv` installed.
2. Run `uv sync --locked --all-groups` to install dependencies.

## Verification Commands
Before submitting a change, run the following to ensure all checks pass:
```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest -q
uv run pip-audit
uv run pre-commit run --all-files
```

## Branch Expectations
* Work should be done on a branch off `main`.
* No destructive Git operations (like force push on `main`).

## Focused-Change Policy
* Keep PRs small and focused on a single issue.
* Unrelated cleanups or formatting changes should be in separate PRs.

## Test Requirements
* All code changes must include tests.
* Coverage must remain at or above 80%.

## Documentation Requirements
* Documentation must accurately reflect the implementation.
* If a security control is added, update the Threat Model and Architecture docs.

## Security-Sensitive Changes
* Any changes to security controls, mitigations, or data policies must be thoroughly reviewed.
* No claims of "enterprise-grade" or "unhackable" security are allowed.

## No Secrets or Private Data
* No passwords, API keys, real personal records, or confidential data may be committed.

## Commit/Push Authorization Policy for Coding Agents
Coding agents must obtain explicit authorization before executing a `git commit` or `git push`.
