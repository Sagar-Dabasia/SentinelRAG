# SentinelRAG

SentinelRAG is an open-source research prototype and portfolio project aimed at systematically understanding and mitigating security vulnerabilities in Retrieval-Augmented Generation (RAG) applications.

Phase 0 — Repository and governance foundation is complete.

Independent audit verdict: PASS WITH WARNINGS.
Verified project progress: 8%.

Phase 1 — Core local RAG baseline is next but has not started.

**Explicit Statement:** No RAG application, database, API, model integration, authentication system, vector index, or UI exists yet.

## Planned Capabilities
In future phases, the project plans to include:
* A FastAPI backend for generation and retrieval.
* A Streamlit research dashboard.
* Local vector search using PostgreSQL + pgvector.
* Local embedding and generation models.
* Vulnerability scanning and evaluation modules.

## Non-goals
* We will not build an "enterprise-ready", "fully secure", or production service.
* We will not use paid APIs or cloud-based model providers (e.g., OpenAI, Anthropic).
* No Kubernetes or complex cloud deployment.

## Security & Ethical Boundaries
* **Local-first and free-only:** The project runs entirely on local hardware using free open-source dependencies.
* No real personal, confidential, or proprietary data will be used. Only synthetic and publicly licensed datasets.
* No passwords, API keys, or live service credentials will be tracked in the repository.

## Prerequisites
* Python 3.14 (or compatible fallback version)
* [uv](https://github.com/astral-sh/uv) (for dependency and environment management)

## Installation
Clone the repository and run:
```bash
uv sync --locked --all-groups
```

## Verification Commands
You can verify the foundation by running:
```bash
# Linting and formatting
uv run ruff check .
uv run ruff format --check .

# Type checking
uv run mypy src tests

# Tests and coverage
uv run pytest -q
uv run pytest -q --cov=sentinelrag --cov-report=term-missing --cov-report=xml --cov-fail-under=80

# Dependency and secret scanning
uv run pip-audit
uv run pre-commit run --all-files
```

## Repository Structure
The repository currently contains the completed Phase 0 governance, documentation, development-tooling, CI, and minimal package foundation. Phase 1 application implementation has not started.
For planned architecture, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation Index
* [Project Charter](docs/PROJECT_CHARTER.md)
* [Architecture](docs/ARCHITECTURE.md)
* [Threat Model](docs/THREAT_MODEL.md)
* [Data Policy](docs/DATA_POLICY.md)
* [Research Questions](docs/RESEARCH_QUESTIONS.md)
* [Evaluation Plan](docs/EVALUATION_PLAN.md)
* [Project Status](docs/PROJECT_STATUS.md)
* [Risk Register](docs/RISK_REGISTER.md)
* [Architecture Decision Records (ADRs)](docs/decisions/)
* [Phase Reports](docs/phases/)

## Links
* [Contributing](CONTRIBUTING.md)
* [Security Policy](SECURITY.md)

## License
This project is licensed under the [Apache License 2.0](LICENSE). Note that future datasets or models may have their own separate licenses.

## Limitations
This is a research project. The security controls will be designed to evaluate specific RAG threats, not to guarantee absolute security against all attacks.
