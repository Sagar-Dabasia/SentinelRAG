# Phase 1A — Compatibility Review & Implementation Roadmap

## 1. Compatibility Matrix

The following table lists the proposed direct dependencies for Phase 1.

| Package / Tool | Purpose | Proposed Constraint | Latest Reviewed | Python 3.14 Compatible | License | Official Source | Windows | Linux/CI | CPU Fallback | Selection Rationale |
|---|---|---|---|---|---|---|---|---|---|---|
| `fastapi` | Web Framework | `>=0.111.0` | 0.111.0 | NOT VERIFIED | MIT | PyPI / Tiangolo | Yes | Yes | N/A | Standard async web framework. |
| `pydantic` | Validation | `>=2.7.0` | 2.8.0 | NOT VERIFIED | MIT | PyPI | Yes | Yes | N/A | Strict type validation. |
| `pydantic-settings` | Configuration | `>=2.3.0` | 2.3.0 | NOT VERIFIED | MIT | PyPI | Yes | Yes | N/A | Environment variable loading. |
| `uvicorn` | ASGI Server | `>=0.30.0` | 0.30.0 | NOT VERIFIED | BSD | PyPI | Yes | Yes | N/A | Runs FastAPI. |
| `httpx` | HTTP Client | `>=0.27.0` | 0.27.0 | NOT VERIFIED | BSD | PyPI | Yes | Yes | N/A | Standard async HTTP client. |
| `python-multipart` | Uploads | `>=0.0.9` | 0.0.9 | NOT VERIFIED | Apache 2.0 | PyPI | Yes | Yes | N/A | Required for FastAPI file uploads. |
| `psycopg` | PostgreSQL Driver | `>=3.2.0` | 3.2.0 | NOT VERIFIED | LGPL | PyPI | Yes | Yes | N/A | Modern async PostgreSQL driver. |
| `sqlalchemy` | ORM | `>=2.0.30` | 2.0.30 | NOT VERIFIED | MIT | PyPI | Yes | Yes | N/A | Database abstraction. |
| `alembic` | DB Migrations | `>=1.13.0` | 1.13.0 | NOT VERIFIED | MIT | PyPI | Yes | Yes | N/A | Manages schema changes. |
| `pgvector` | DB Vector SDK | `>=0.3.0` | 0.3.0 | NOT VERIFIED | MIT | PyPI | Yes | Yes | N/A | Official pgvector Python integration. |
| `streamlit` | Research Dashboard | `>=1.36.0` | 1.36.0 | NOT VERIFIED | Apache 2.0 | PyPI | Yes | Yes | N/A | Rapid research UI. |
| `pypdf` | PDF Parsing | `>=4.2.0` | 4.2.0 | NOT VERIFIED | BSD | PyPI | Yes | Yes | N/A | Native Python PDF extraction. |
| `sentence-transformers` | Embeddings SDK | `>=3.0.0` | 3.0.0 | NOT VERIFIED | Apache 2.0 | PyPI | Yes | Yes | Yes | Industry standard local embeddings. |
| `torch` | Tensor Lib | `2.9.1` | 2.9.1 | NOT VERIFIED | BSD | PyPI | Yes | Yes | Yes | Validated CPU baseline. |
| `transformers` | Inference | `4.44.0` | 4.44.0 | NOT VERIFIED | Apache 2.0 | PyPI | Yes | Yes | Yes | Required for compatible local model inference. |

## 2. Model Compatibility

| Component | Target Model | Revision Hash | Compatibility Status |
| :--- | :--- | :--- | :--- |
| Core Embedding | `BAAI/bge-small-en-v1.5` | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` | Confirmed. Size: ~133MB |

* **Security Invariant Verified:** `trust_remote_code=False` is enforced in initialization contracts.
* **Revision Strategy:** Model must be pulled using the immutable hash, not `main`.

## 3. Storage Compatibility

| Component | Target Version | Selection Notes |
| :--- | :--- | :--- |
| PostgreSQL | `16` | LTS Support, pgvector compatibility. |
| pgvector ext | `0.8.6` | 0.8.6 contains the latest verified security correction. |

## 4. Python Environment Probes

* **Python 3.14 Compatibility Note:** The broad-stack experiment failed because testing the entire Phase 1 stack prematurely introduced blocking issues (e.g., `tokenizers` build failure on Python 3.14).
* **Staged Verification:** To prevent premature full-stack blockages, the remaining ecosystem is deferred to just-in-time staged verification gates (1C, 1D, 1F).

## 5. Audit Results

* **Phase 1B Dependencies:** VERIFIED. Pydantic 2.13.4, Pydantic Settings 2.14.2, HTTPX 0.28.1 were successfully imported without network access using `uv run --group phase1b-compat python scripts/verify_phase1b_compatibility.py`.
* **Full Stack Verification:** DEFERRED to subphases.

## 6. Phase 1 Implementation Roadmap

Phase 1 is divided into small, auditable subphases. No implementation proceeds until the prior phase's exit gate passes.

### Phase 1A — Compatibility review
* **Objective:** Define the technical compatibility baseline and implementation roadmap. (This document).

### Phase 1B — Configuration and model-provider contracts
* **Objective:** Establish the foundational settings and external model interface abstractions.
* **Expected modules:** Central settings (`pydantic-settings`), provider protocol, Ollama adapter, LM Studio-compatible adapter.
* **Non-goals:** No generation logic or prompt templating.
* **Security invariants:** No external provider enabled by default. No network call during package import.
* **Required tests:** Unit tests for failure handling, timeouts, and API contract parsing.
* **Required documentation:** API module docstrings.
* **Exit gate:** Tests pass, coverage maintained, lockfile stable.
* **Dependencies on prior subphases:** 1A.

### Phase 1C — PostgreSQL, pgvector and persistence foundation
* **Objective:** Set up the database schema and scope-aware repository pattern.
* **Expected modules:** Database startup (Docker Compose), SQLAlchemy models, Alembic migrations, Vector schema, Repositories, Scope-aware interfaces.
* **Non-goals:** No application logic or file ingestion.
* **Security invariants:** Database binding restricted to localhost. Queries require explicit scope context.
* **Required tests:** Integration tests running against an ephemeral CI container testing migrations and CRUD operations.
* **Required documentation:** Schema documentation.
* **Exit gate:** Migrations apply cleanly on an empty container, integration tests pass.
* **Dependencies on prior subphases:** 1B.

### Phase 1D — Safe ingestion, chunking and embeddings
* **Objective:** Implement deterministic parsing and embedding pipelines.
* **Expected modules:** Allowlisted ingestion logic, `pypdf`/text parsing, deterministic chunking logic, local embeddings (`sentence-transformers`), provenance tracking.
* **Non-goals:** No retrieval or chat APIs.
* **Security invariants:** Enforced MIME validation, size limits, and safe generated storage names. `trust_remote_code=False` enforced.
* **Required tests:** Determinism tests for chunking, negative tests for invalid files (oversized, bad MIME).
* **Required documentation:** Chunking strategy and model provenance.
* **Exit gate:** Document ingestion succeeds end-to-end locally and in CI.
* **Dependencies on prior subphases:** 1C.

### Phase 1E — Retrieval, generation and citations
* **Objective:** Build the core RAG logic.
* **Expected modules:** Scope-aware retrieval, prompt-template versioning, evidence-linked generation, citation validation, insufficient-evidence abstention.
* **Non-goals:** No user-facing API or UI.
* **Security invariants:** Generation service receives only authorized chunks from the server. Citation validation confirms chunks match retrieval.
* **Required tests:** Mocked generation tests confirming abstention and citation matching. Scope isolation tests.
* **Required documentation:** Prompt templates.
* **Exit gate:** Core RAG pipeline executes successfully in unit/integration tests.
* **Dependencies on prior subphases:** 1D.

### Phase 1F — Basic API, dashboard and end-to-end gate
* **Objective:** Expose the pipeline for local research execution.
* **Expected modules:** Minimal FastAPI endpoints, basic Streamlit interface, document management, query interface, source display.
* **Non-goals:** No production frontend security, no external network exposure.
* **Security invariants:** API endpoints enforce scope context logic (hardcoded to "default" for Phase 1).
* **Required tests:** End-to-end local test.
* **Required documentation:** Phase report and audit request.
* **Exit gate:** Complete end-to-end execution of the RAG pipeline via the dashboard.
* **Dependencies on prior subphases:** 1E.
