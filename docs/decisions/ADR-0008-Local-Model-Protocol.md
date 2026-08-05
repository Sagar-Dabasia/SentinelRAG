# ADR 0008: Local Model Protocol and Adapter Architecture

## Status
Accepted

## Context
In Phase 1B, we needed to establish the foundational contract for interacting with local LLM providers (Ollama, LM Studio). Because these providers frequently change their APIs and behaviors, directly coupling application logic to their specific HTTP endpoints would create maintenance overhead and fragility.

## Decision
We decided to implement a strict `Provider` protocol and an adapter architecture (`OllamaAdapter`, `LMStudioAdapter`, `DisabledProvider`). The protocol defines a standardized `generate()` method taking a `GenerationRequest` and returning a unified `GenerationResponse`.

## Consequences
- **Positive:** Application logic remains agnostic to the underlying provider API. Adding new providers requires only a new adapter.
- **Positive:** Centralized error handling via a taxonomy of `ProviderError`s (e.g., `ProviderHttpError`, `ProviderProtocolError`).
- **Negative:** Additional abstraction overhead and mapping boilerplate.
