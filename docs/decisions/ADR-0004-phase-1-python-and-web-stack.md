# ADR-0004: Phase 1 Python and Web Stack

* **Status:** Accepted
* **Date:** 2026-08-05
* **Context:** SentinelRAG requires a robust, async-capable web and configuration stack for its Phase 1 local baseline. The current project enforces Python 3.14 and uses `uv` for dependency management. The chosen stack must support local deployment, structured configuration, and provide a basic research dashboard without claiming production frontend security.
* **Decision:**
    * **Python Version:** Python 3.14 (Compatibility currently marked as NOT VERIFIED for the complete downstream ecosystem; may require fallback to 3.13 during implementation).
    * **Web Framework:** FastAPI, Pydantic, Pydantic Settings, Uvicorn, HTTPX, `python-multipart`.
    * **Research Dashboard:** Streamlit (used strictly as an internal research interface, not a secure production frontend).
    * **Configuration Approach:** Centralized using Pydantic Settings.
    * **Logging Approach:** Python standard library `logging` with structured JSON formatting for security-event metadata boundaries. Prohibit logging of document content or user secrets.
    * **Dependency-versioning policy:** Strict pinning via `uv.lock`.
* **Evidence:**
    * **FastAPI (0.111.0+) / Pydantic (2.x) / Uvicorn (0.30.0+) / HTTPX (0.27.0+):** Official PyPI metadata and FastAPI documentation. Supported in modern Python, but explicit 3.14 support is NOT VERIFIED. License: MIT. Windows/Linux/CI compatible.
    * **Streamlit (1.36.0+):** Official PyPI metadata. Explicit 3.14 support NOT VERIFIED. License: Apache 2.0.
* **Alternatives considered:**
    * Flask / Django: Rejected due to lack of native fast async support (Flask) or unnecessary weight (Django) when building an API-first backend.
    * External Observability Platform (e.g. Datadog): Rejected. Not justified for a local-first research prototype.
* **Security consequences:** Framework-owned abstractions will be avoided for provider interfaces. Business logic will remain outside API routes.
* **Reproducibility consequences:** Strict `uv.lock` pinning ensures CI and local environments match exactly.
* **Operational consequences:** No external network calls during import. Standard library logging reduces dependency overhead.
* **Revisit conditions:** If Python 3.14 causes unresolvable build failures for binary dependencies (e.g., Pydantic core), fallback to 3.13 will be triggered in a separate task.
