# ADR-0010: Offline MockTransport Testing

* **Status:** Proposed — pending independent Phase 1B audit
* **Date:** 2026-08-05
* **Context:** Testing the local model adapters requires simulating HTTP responses. Using real network connections or tools like `pytest-asyncio` introduces external dependencies, unreliability, and non-compliance with the strictly offline, locked-down Phase 1 testing requirements.
* **Decision:** We use `httpx.MockTransport` coupled with standard library `asyncio.run()` to test provider HTTP streams. We do not patch `AsyncClient.stream`.
* **Evidence:** The test suite in `tests/unit/models` effectively simulates chunked streaming responses, HTTP errors, and timeouts safely without any network egress.
* **Alternatives:** Using `respx` or `responses`. Rejected to minimize test dependencies and fully control the stream behavior natively through HTTPX.
* **Security consequences:** Ensures tests will never leak data to a real provider, avoiding test contamination and network leakage.
* **Operational consequences:** Requires manual construction of HTTPX Response objects in tests, but provides maximal control and predictability.
* **Revisit conditions:** Unlikely to be revisited as it perfectly fits the offline evaluation requirements.
