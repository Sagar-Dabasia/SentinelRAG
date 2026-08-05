# ADR-0006: Local Model and Embedding Stack

* **Status:** Proposed — deferred to Phase 1D compatibility gate
* **Date:** 2026-08-05
* **Context:** SentinelRAG requires an initial embedding implementation fitting an RTX 4060 (8 GB VRAM) with a CPU fallback. Generation requires local interfaces for Ollama and LM Studio. Actual validation and installation are deferred to Phase 1D to comply with staged compatibility.
* **Decision:**
    * **Provider-Interface Design:** Application-owned abstractions. We will build direct HTTP adapters using `httpx`.
    * **Ollama & LM Studio Adapters:** Direct HTTP adapters (Planned).
    * **Initial Embedding Library:** `sentence-transformers` (PyTorch) (Planned).
    * **Exact Embedding Model:** `BAAI/bge-small-en-v1.5` remains the preferred candidate.
    * **Verified Candidate Revision:** `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`
    * **Candidate Licence:** MIT
    * **Candidate Dimension:** 384
    * **Implementation Status:** No model has been downloaded or initialized. No embedding implementation exists.
* **Evidence:**
    * Actual Sentence Transformers and PyTorch compatibility is deferred to Phase 1D.
* **Alternatives considered:**
    * **Alternative Provider SDKs:** `openai` Python SDK (Rejected because it introduces external provider defaults).
* **Security consequences:** `trust_remote_code=False` will be enforced by policy, though it is not yet implemented in code.
* **Reproducibility consequences:** Pinning embedding model revision hashes ensures stable vectors.
* **Operational consequences:** Running embeddings locally via PyTorch will require compiling/downloading large torch binaries, deferred to Phase 1D.
* **Revisit conditions:** Exact dependencies (PyTorch, transformers) will be locked and verified in Phase 1D.
