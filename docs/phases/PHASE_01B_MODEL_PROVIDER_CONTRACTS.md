# Phase 1B: Model Provider Contracts

## Status
**Completed**

## Objective
Establish the foundational central configuration and provider abstractions for local LLMs (Ollama, LM Studio) prior to building the retrieval pipeline. Ensure that SentinelRAG can deterministically generate text from local models while adhering to strict security constraints (offline-only testing, loopback-only endpoints, strict character/token limits).

## Implementation Notes
- **Central Configuration**: Created `SentinelSettings` using Pydantic, enforcing environment variable overrides and loopback-only model endpoints (`127.0.0.1`, `::1`, `localhost`).
- **Provider Protocol**: Defined a `Provider` protocol and `GenerationRequest`/`GenerationResponse` contracts to abstract provider-specific payload differences.
- **Provider Adapters**: Implemented `OllamaAdapter`, `LMStudioAdapter`, and a fail-safe `DisabledProvider`.
- **Security Constraints**: Built custom `http.py` wrapper over `httpx` enforcing maximum streaming byte limits to prevent memory exhaustion and DoS from unbound models.
- **Offline Testing**: Authored `MockTransport` to completely mock provider HTTP streams, proving safety limits without making real network calls.

## Output
- `src/sentinelrag/config/settings.py`
- `src/sentinelrag/models/contracts.py`
- `src/sentinelrag/models/provider.py`
- `src/sentinelrag/models/factory.py`
- `src/sentinelrag/models/http.py`
- `src/sentinelrag/models/ollama.py`
- `src/sentinelrag/models/lm_studio.py`
- `src/sentinelrag/models/disabled.py`
- ADR-0008, ADR-0009, ADR-0010

## Next Phase
Phase 1C: Embedding models and vector repository initialization.
