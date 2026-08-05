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
* No silent fallback for misspelled config.
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

## 15. Test matrix
* `httpx.MockTransport` offline tests.
* Configuration edge cases.
* Provider serialization, lifecycle (`aclose()`), validation, limits, retries.
* SentinelRAG governance constraints.

## 16. Coverage
* 100% config coverage.
* 100% models coverage.
* >80% overall repository branch coverage.

## 17. Exact verification commands and exit codes
* `uv run ruff check .` - 0
* `uv run ruff format --check .` - 0
* `uv run mypy src tests scripts` - 0
* `uv run pytest -q` - 0
* `uv run python scripts/verify_phase1b_compatibility.py` - 0

## 18. Security implications
* Model interactions are restricted to the local loopback interface, eliminating unauthorized remote queries.
* Strict validation limits minimize prompt injection size effects and memory exhaustion (DoS).
* Offline testing guarantees no leaks.

## 19. Limitations
* This phase only establishes the client protocol. RAG architecture is still missing.
* Token count validation is purely dependent on provider feedback.

## 20. Requirements-to-evidence matrix
* Contracts Implemented? Yes (`sentinelrag.models`).
* Validation Constraints Enforced? Yes (`sentinelrag.config`).
* Tests Pass Offline? Yes (`httpx.MockTransport`).

## 21. Candidate commit: `PENDING`
## 22. Push: `PENDING`
## 23. External audit: `PENDING`
