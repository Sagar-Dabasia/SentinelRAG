# ADR-0005: PostgreSQL and Vector Storage

* **Status:** Accepted
* **Date:** 2026-08-05
* **Context:** The Phase 1 baseline requires a relational and vector storage solution. The approved architecture dictates PostgreSQL with pgvector unless incompatibility is verified.
* **Decision:**
    * **Database Engine:** PostgreSQL 16
    * **Vector Extension:** pgvector (0.8.6)
    * **Local Startup Strategy:** Docker Compose will be used to provide a version-pinned local PostgreSQL/pgvector container.
    * **CI Database Strategy:** CI will spin up the exact same Docker Compose container to ensure environment parity.
    * **ORM & Migrations:** SQLAlchemy 2.x and Alembic.
    * **Driver:** psycopg 3 (psycopg[binary] for local/CI fallback).
    * **Integration:** Official Python `pgvector` library for SQLAlchemy integration.
    * **Migration-Testing Strategy:** Migrations will be tested as part of the integration test suite running against the ephemeral CI container.
    * **Vector Dimension and Metadata Enforcement:** Enforced at the SQLAlchemy schema layer (e.g. `Vector(384)`) and managed via Alembic migrations.
    * **Secret Management:** Connection configuration passed exclusively via environment variables (no hardcoded credentials).
* **Evidence:**
    * **PostgreSQL 16 & pgvector:** Official Docker Hub `pgvector/pgvector:pg16` image. License: PostgreSQL/MIT. Known compatible with Windows (via WSL2/Docker) and Linux.
    * **SQLAlchemy (2.x) / Alembic / psycopg 3:** Official PyPI metadata. Python 3.14 support is NOT VERIFIED. License: MIT / LGPL.
* **Alternatives considered:**
    * **Temporary in-memory vector stores (e.g., Chroma, FAISS):** Rejected. The project roadmap mandates PostgreSQL/pgvector. Adopting a temporary store introduces throw-away work and delays schema design.
* **Security consequences:** Secrets will not be checked in. The database will bind only to localhost in local development.
* **Reproducibility consequences:** Docker Compose guarantees everyone runs the exact same pgvector version.
* **Operational consequences:** Requires Docker Desktop or equivalent on Windows development machines.
* **Revisit conditions:** If psycopg 3 binary builds fail on Python 3.14, a downgrade to Python 3.13 will be requested.
