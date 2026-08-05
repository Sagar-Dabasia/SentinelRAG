# ADR-0008: Local Model Protocol and Adapter Architecture

* **Status:** Proposed — pending independent Phase 1B audit
* **Date:** 2026-08-05
* **Context:** In Phase 1B, we needed to establish the foundational contract for interacting with local LLM providers (Ollama, LM Studio). Because these providers frequently change their APIs and behaviors, directly coupling application logic to their specific HTTP endpoints would create maintenance overhead and fragility.
* **Decision:** We decided to implement a strict `Provider` protocol and an adapter architecture (`OllamaAdapter`, `LMStudioAdapter`, `DisabledProvider`). The protocol defines a standardized `generate()` method taking a `GenerationRequest` and returning a unified `NormalizedResponse`.
* **Evidence:** Implementation in `sentinelrag.models.contracts` and passing offline unit tests demonstrating isolation from raw HTTP payloads.
* **Alternatives:** Using `openai` SDK directly, but this introduces external provider defaults and less strict limits.
* **Security consequences:** Application logic remains isolated from the raw provider API, reducing parsing vulnerabilities. It allows for strict token and character bounds.
* **Operational consequences:** Adds abstraction overhead but centralizes error handling and timeouts.
* **Revisit conditions:** Revisit when external API endpoints (like OpenAI) are authorized or if local providers adopt a truly unified standard.
