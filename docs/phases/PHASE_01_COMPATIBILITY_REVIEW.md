# Phase 1A — Compatibility Review & Implementation Roadmap

## Objective
Define the technical compatibility baseline and implementation roadmap for Phase 1. Ensure Python 3.14 compatibility explicitly for the immediate next phase without blocking on the complete stack.

## Starting commit
`f6b2cf1724d811e8d1183bb89aaf4a68340fec64`

## Failed broad-stack experiment
The initial compatibility review attempted to approve and verify the entire Phase 1 stack (FastAPI, Streamlit, PyTorch, Sentence-Transformers, PostgreSQL drivers) upfront. This broad-stack experiment failed because testing the entire Phase 1 stack prematurely introduced blocking issues (e.g., `tokenizers` build failure on Python 3.14).

## Failed remediation commit
Commit `0be9e4cb6b0ff500381e0f14f7431187b7b7319e` failed the audit due to contradictions in ADR statuses and missing executable governance tests.

## Audit of commit
Commit `f6b2cf1724d811e8d1183bb89aaf4a68340fec64` attempted to establish staged compatibility but lacked proper executable governance contracts and had inaccurate risk register updates.

## Root causes
Attempting to enforce full-stack ahead-of-time compatibility on an evolving Python version (3.14) triggered unrelated binary build failures (e.g. `tokenizers`) that blocked progress on unrelated core configuration tasks.

## Staged compatibility decision
To prevent premature full-stack blockages, the remaining ecosystem is deferred to just-in-time staged verification gates (1C, 1D, 1F).

## Current Phase 1B exact dependency matrix
| Package | Version |
|---|---|
| `pydantic` | `==2.13.4` |
| `pydantic-settings` | `==2.14.2` |
| `httpx` | `==0.28.1` |

## Python 3.14 evidence
Python 3.14 is verified solely for Phase 0 tooling and the Phase 1B exact dependency matrix. We do not claim full Phase 1 compatibility.

## Verifier design
`verify_phase1b_compatibility.py` uses `tomllib` to parse the exact `phase1b-compat` requirements. It enforces strict `==` pins. A context manager blocks `socket.socket.connect` and `socket.create_connection` to ensure no network calls on import. Another context manager scrubs secrets during verification to ensure secret independence.

## Local verification evidence
Local verification passed successfully. `pydantic`, `pydantic-settings`, and `httpx` were imported without network access and without secrets. Exact installed versions matched expected requirements.

## Deferred Phase 1C decisions
PostgreSQL, `pgvector`, SQLAlchemy, Alembic, and `psycopg` versions, digests, and configurations are deferred to Phase 1C. `Vector(384)` remains the candidate dimension. No database code is implemented yet.

## Deferred Phase 1D decisions
`sentence-transformers`, `torch`, `transformers`, and the `BAAI/bge-small-en-v1.5` candidate model (revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`) are deferred to Phase 1D.

## Deferred Phase 1F decisions
`fastapi`, `uvicorn`, `python-multipart`, and `streamlit` validations are deferred to Phase 1F.

## Security implications
Staged gates prevent dependency compromise during early phases. Network blocking ensures no telemetry on import.

## Limitations
FastAPI, Streamlit, and PyTorch compatibility with Python 3.14 is currently NOT VERIFIED. If future phases fail on 3.14, fallback to 3.13 may be required.

## Requirements-to-evidence matrix
| Requirement | File | Verification command/test | Result |
| ----------- | ---- | ------------------------- | ------ |
| Enforce Python 3.14 | `pyproject.toml` | `pytest tests/unit/test_phase1a_governance_contract.py` | Pass |
| Repair Phase 1B verifier | `scripts/verify_phase1b_compatibility.py` | `python scripts/verify_phase1b_compatibility.py` | Pass |
| Add executable tests for governance | `tests/unit/test_phase1a_governance_contract.py` | `pytest tests/unit/test_phase1a_governance_contract.py` | Pass |
| Correct ADR contradictions | `docs/decisions/ADR-0001...` | `pytest tests/unit/test_phase1a_governance_contract.py` | Pass |
| Correct project status/risks | `docs/PROJECT_STATUS.md` | `pytest tests/unit/test_phase1a_governance_contract.py` | Pass |
| Staged Phase 1A report | `docs/phases/PHASE_01...` | `pytest tests/unit/test_phase1a_governance_contract.py` | Pass |
| Phase 1B unapproved | `docs/PROJECT_STATUS.md` | `pytest tests/unit/test_phase1a_governance_contract.py` | Pass |

## External audit: PENDING
