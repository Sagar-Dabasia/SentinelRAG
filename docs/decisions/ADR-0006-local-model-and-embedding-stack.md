# ADR-0006: Local Model and Embedding Stack

* **Status:** Accepted
* **Date:** 2026-08-05
* **Context:** SentinelRAG requires an initial embedding implementation fitting an RTX 4060 (8 GB VRAM) with a CPU fallback. Generation requires local interfaces for Ollama and LM Studio (OpenAI-compatible endpoints). The solution must not silently call external providers or allow arbitrary remote code execution without strict constraints.
* **Decision:**
    * **Provider-Interface Design:** Application-owned abstractions. We will build direct HTTP adapters using `httpx` rather than importing hosted-provider SDKs like `openai` or `ollama-python`. This ensures no accidental network calls on import and strict timeout/retry limits.
    * **Ollama Adapter:** Uses the `/api/generate` and `/api/chat` endpoints.
    * **LM Studio Adapter:** Uses the OpenAI-compatible `/v1/chat/completions` endpoint.
    * **Initial Embedding Library:** `sentence-transformers` (PyTorch).
    * **Exact Embedding Model:** `BAAI/bge-small-en-v1.5`
    * **Revision Policy:** Tied to the immutable model commit hash. Model files must be downloaded deterministically. `trust_remote_code=False` is strictly enforced.
    * **CPU/GPU Fallback:** PyTorch handles CUDA/CPU fallback naturally.
    * **Model Provenance Recording:** The exact identifier and revision hash will be tracked in config and logged to experiment artifacts.
* **Evidence:**
    * **BAAI/bge-small-en-v1.5:** Official HuggingFace repository. License: MIT. Dimension: 384. Context limit: 512. Normalization required. Prefix for query: `Represent this sentence for searching relevant passages: `. Memory: < 200MB, easily fits on 8GB VRAM or CPU. Requires no remote custom code.
    * **Sentence-Transformers (3.x):** Official PyPI. License: Apache 2.0. Python 3.14 support NOT VERIFIED.
* **Alternatives considered:**
    * **Alternative Embedding Model:** `nomic-ai/nomic-embed-text-v1.5` (Rejected because it relies on `trust_remote_code=True` natively in older HF versions, violating security constraints, despite having an 8192 context window).
    * **Alternative Provider SDKs:** `openai` Python SDK (Rejected because it introduces external provider defaults and broader surface area than required for local endpoints).
* **Security consequences:** `trust_remote_code=False` prevents arbitrary execution from model repos. Direct HTTP adapters prevent accidental telemetry to external SaaS providers.
* **Reproducibility consequences:** Pinning embedding model revision hashes ensures stable vectors.
* **Operational consequences:** Running embeddings locally via PyTorch will require compiling/downloading large torch binaries, which must be tracked in CI caching.
* **Revisit conditions:** If PyTorch does not support Python 3.14 on Windows locally, fallback to 3.13 will be required.
