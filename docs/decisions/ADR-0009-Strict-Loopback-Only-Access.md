# ADR 0009: Strict Loopback-Only Access

## Status
Accepted

## Context
SentinelRAG is a local-first application dealing with sensitive, highly-privileged RAG documents. The underlying LLM providers (Ollama, LM Studio) must not be exposed to the public internet, nor should SentinelRAG attempt to connect to external unverified IPs to prevent SSRF or external exfiltration.

## Decision
We enforce a strict loopback-only rule for provider endpoints in the `SentinelSettings` configuration. Only `127.0.0.1`, `::1`, `[::1]`, and `localhost` are accepted.

## Consequences
- **Positive:** Reduced attack surface by enforcing local communication.
- **Positive:** Prevents accidental or malicious redirection to external endpoints.
- **Negative:** Limits deployment flexibility (e.g. running the LLM provider on a separate network machine is not supported by default, unless configured via a local proxy).
