# ADR-0005: PostgreSQL and Vector Storage

* **Status:** Proposed — deferred to Phase 1C compatibility gate
* **Date:** 2026-08-05
* **Context:** The Phase 1 baseline requires a relational and vector storage solution. PostgreSQL plus pgvector remains the preferred planned architecture. However, to comply with staged compatibility, actual validation is deferred.
* **Decision:**
    * **Database Engine:** PostgreSQL 16 (Planned)
    * **Vector Extension:** pgvector (Planned)
    * **Local Startup Strategy:** Docker Compose will be used. Exact PostgreSQL version, pgvector release, container tag, and digest will be verified in Phase 1C.
    * **Vector Dimension:** `Vector(384)` is the current embedding-model candidate dimension, not yet a migration.
    * **Implementation Status:** No Docker or database implementation exists.
* **Evidence:**
    * Floating tags like `pg16` are not reproducible without an exact manifest digest. A pinned digest will be established in Phase 1C.
* **Alternatives considered:**
    * **Temporary in-memory vector stores:** Rejected. The project roadmap mandates PostgreSQL/pgvector.
* **Security consequences:** Secrets will not be checked in. The database will bind only to localhost in local development.
* **Reproducibility consequences:** Docker Compose guarantees everyone runs the exact same pgvector version once the digest is pinned in Phase 1C.
* **Operational consequences:** Requires Docker Desktop or equivalent on Windows development machines.
* **Revisit conditions:** Exact dependencies (SQLAlchemy, Alembic, psycopg) will be locked and verified in Phase 1C.
