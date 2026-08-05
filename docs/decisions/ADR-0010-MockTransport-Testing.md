# ADR 0010: MockTransport Offline Testing

## Status
Accepted

## Context
Phase 1B integration tests for external providers require HTTP calls. However, our security and governance rules forbid real external network calls during tests to ensure CI reliability, speed, and strict offline capability.

## Decision
We use `httpx.MockTransport` directly in our adapters during testing instead of `unittest.mock.patch` on `httpx.AsyncClient` methods or external libraries like `respx`. 

## Consequences
- **Positive:** Tests are completely offline and deterministic.
- **Positive:** No new testing dependencies required (e.g. `respx`).
- **Positive:** Real HTTP streams can be mocked precisely using our custom `MockStreamResponse` to verify limits and limits enforcement.
- **Negative:** Maintaining custom `MockTransport` logic requires a bit more boilerplate per test file.
