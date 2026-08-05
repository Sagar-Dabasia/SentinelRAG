# ADR-0004: Phase 1 Python and Web Stack

* **Status:** Proposed — pending independent Phase 1A audit
* **Date:** 2026-08-05
* **Context:** SentinelRAG requires a robust, async-capable web and configuration stack for its Phase 1 local baseline. The current project enforces Python 3.14. To prevent premature full-stack failures, we are applying staged compatibility. This ADR currently approves only the Phase 1B dependencies.
* **Decision:**
    * **Python Version:** Python 3.14.
    * **Phase 1B Dependencies:** Pydantic 2.13.4, Pydantic Settings 2.14.2, HTTPX 0.28.1.
    * **Provider Abstraction:** Application-owned provider protocol and direct HTTP adapters.
    * **Network Constraints:** No network at import. No provider enabled by default.
    * **Deferred Approvals:** No FastAPI or Uvicorn approval yet. FastAPI and Streamlit validation deferred to Phase 1F.
    * **Configuration Approach:** Centralized using Pydantic Settings.
    * **Dependency-versioning policy:** Strict pinning via `uv.lock`.
* **Evidence:**
    * **Pydantic (2.13.4) / Pydantic Settings (2.14.2) / HTTPX (0.28.1):** Successfully verified and imported via `verify_phase1b_compatibility.py` under Python 3.14. No network connections at import time.
* **Alternatives considered:**
    * Full-stack ahead-of-time compatibility: Rejected due to causing blocked CI pipelines for future-phase dependencies (e.g. `tokenizers` build failure).
* **Security consequences:** Application-owned provider protocol isolates the application from external SDK vulnerabilities.
* **Operational consequences:** No external network calls during import are strictly enforced by the compatibility verifier.
* **Revisit conditions:** FastAPI and Streamlit will be revisited in Phase 1F.
