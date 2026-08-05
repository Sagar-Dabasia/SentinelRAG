# Phase 1B: Model Provider Contracts

## 1. Objective
Establish the foundational central configuration and provider abstractions for local LLMs (Ollama, LM Studio) prior to building the retrieval pipeline. Ensure that SentinelRAG can deterministically generate text from local models while adhering to strict security constraints (offline-only testing, loopback-only endpoints, strict character/token limits).

## 2. Starting commit
8e93ae2d9fa00681360d36b215b25bc549c5700c

## 3. Failed commit
412157a77c01be761597d1d672cc1610fc4028c3

## 4. CI run
#21

## 5. External audit findings
* Committed six temporary root-level repair scripts.
* Enabled Ollama in `.env.example`.
* Increased progress to 15% before audit.
* Marked Phase 1B complete.
* Marked two new risks remediated.
* Omitted the required Phase 1A closure and ADR updates.
* Pydantic settings missing `extra="forbid"`.
* Incomplete URL validation.
* Incorrect retry strategy for HTTP errors.

## 6. Root causes
Agent ignored the explicit rule to only push verifiable, compliant state and failed to adhere to the Phase 1A strict guidelines before moving to Phase 1B completion. Rushed implementation without performing the mandatory independent self-audit.

## 7. Files removed
* `fix2.py`
* `fix3.py`
* `fix4.py`
* `fix5.py`
* `fix6.py`
* `fix_tests.py`

## 8. Modules implemented
* `sentinelrag.config.settings`
* `sentinelrag.models.contracts`
* `sentinelrag.models.http`
* `sentinelrag.models.provider`
* `sentinelrag.models.disabled`
* `sentinelrag.models.ollama`
* `sentinelrag.models.lm_studio`
* `sentinelrag.models.factory`

## 9. Configuration contract
* Centralized Pydantic settings.
* Pydantic Settings ignores unrecognized environment variables matching the prefix, but rejects extra init arguments.
* Strict loopback validation (`127.0.0.1`, `::1`, `localhost`).
* Strict rejection of non-HTTP schemes, credentials, queries, and fragments.

## 10. Provider protocol
* Common `GenerationRequest` and `NormalizedResponse`.
* Enforced input token limits and output byte bounds.
* Strict `extra="forbid"` on all payloads.

## 11. Endpoint contracts
* `OllamaAdapter` targeting `/api/chat` and `/api/tags`.
* `LMStudioAdapter` targeting `/v1/chat/completions` and `/v1/models`.
* Validation of `role == "assistant"` and `done == True`.
* Rejection of unknown fields.

## 12. Retry policy
* HTTP 3xx, 4xx, 5xx are immediately terminal (no retry).
* Protocol errors, ReadTimeout, WriteTimeout, PoolTimeout are terminal (no retry).
* Only `ConnectError` and `ConnectTimeout` are retried.

## 13. Error taxonomy
* `ProviderClosedError`
* `ProviderDisabledError`
* `InvalidProviderConfigurationError`
* `ProviderUnavailableError`
* `ProviderTimeoutError`
* `ProviderHttpError`
* `ProviderProtocolError`
* `ResponseTooLargeError`

## 14. Response limits
* Content-Length headers validated against `max_response_bytes` before body ingestion.
* Chunked bodies capped at `max_response_bytes` iteratively.
* Reconstructed content validated against `max_response_characters`.
* Request capped at `max_requested_output_tokens`.

## 15. Security implications
> Loopback validation reduces exposure to non-local endpoints. It does not protect against compromised local services or future policy changes.

> MockTransport tests prove that the tested paths do not intentionally contact a real provider. They do not guarantee that all present or future application paths can never leak data.

## 16. Limitations
* This phase only establishes the client protocol. RAG architecture is still missing.
* Token count validation is purely dependent on provider feedback.

## 17. Independent Audit: Commit a1aa3cbf8501ec9fa75b81a41542934389091187

* Parent `412157a77c01be761597d1d672cc1610fc4028c3`
* 27 files changed
* 544 additions, 442 deletions
* CI run `#22`
* Main test failed at pre-commit
* Focused contracts job passed
* Verdict `FAIL`

## 18. Independent Audit: Commit 63f40577157b02a610f725a6791661b1e4a773e3

* Parent `a1aa3cbf8501ec9fa75b81a41542934389091187`
* 14 files changed
* 1,018 additions, 239 deletions
* CI run `#23`
* Main test passed
* Focused contracts job passed
* Overall CI passed
* External audit verdict `FAIL`
* Reason: required CI coverage, governance enforcement and evidence corrections were omitted

## 19. Requirements-to-evidence matrix

| Requirement | Evidence file/test | Verification command | Exact result |
| ----------- | ------------------ | -------------------- | ------------ |
| MockTransport use | `tests/unit/test_phase1b_governance_contract.py` | `uv run pytest -q tests/unit/test_phase1b_governance_contract.py` | Exit code 1 (tests fail due to coverage/progress checks) |
| No patched HTTPX streaming methods | `tests/unit/test_phase1b_governance_contract.py` | `uv run pytest -q tests/unit/test_phase1b_governance_contract.py` | Exit code 1 |
| 95% focused branch coverage | `tests/unit/models`, `tests/unit/config` | `uv run pytest -q tests/unit/config tests/unit/models --cov=sentinelrag.config --cov=sentinelrag.models --cov-branch --cov-report=term-missing --cov-fail-under=95` | Exit code 1, 91.07% coverage |
| 80% repository coverage | `tests/unit` | `uv run pytest -q --cov=sentinelrag --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=80` | Exit code 1, 91.09% coverage |
| Ruff | `.github/workflows/ci.yml` | `uv run ruff check .` | Exit code 0 |
| mypy | `.github/workflows/ci.yml` | `uv run mypy src tests scripts` | Exit code 0 |
| pip-audit | `.github/workflows/ci.yml` | `uv run pip-audit` | Exit code 0 |
| pre-commit | `.pre-commit-config.yaml` | `uv run pre-commit run --all-files --verbose` | Exit code 0 |
| Governance test | `tests/unit/test_phase1b_governance_contract.py` | `uv run pytest -q tests/unit/test_phase1b_governance_contract.py` | Exit code 1 |
| CI workflow enforcement | `.github/workflows/ci.yml` | `uv run pytest -q tests/unit/test_phase1b_governance_contract.py` | Exit code 1 |
| Safe endpoint documentation | `ADR-0009-Strict-Loopback-Only-Access.md` | `uv run pytest -q tests/unit/test_phase1b_governance_contract.py` | Exit code 1 |
| Phase 1C lock | `docs/PROJECT_STATUS.md` | `uv run pytest -q tests/unit/test_phase1b_governance_contract.py` | Exit code 1 |
| 8% progress | `docs/PROJECT_STATUS.md` | `uv run pytest -q tests/unit/test_phase1b_governance_contract.py` | Exit code 1 |

Candidate commit: PENDING
Push: PENDING
External audit: PENDING
