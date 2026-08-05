# ADR-0007: Phase 1 Scope-Aware Data Model

* **Status:** Accepted
* **Date:** 2026-08-05
* **Context:** SentinelRAG Phase 1 will not implement multi-user authentication or authorization, but the data model must be designed so that Phase 2 can migrate to full tenant isolation without destructive data migrations. Database queries must not depend on a hidden global scope.
* **Decision:**
    * **Single-Workspace Behaviour:** Phase 1 will operate using a single local default workspace (e.g., `workspace_id = "default"`).
    * **Explicit Scope-Context Interface:** All repository interfaces (CRUD, retrieval) must accept an explicit scope context object. The backend will enforce this context at the query level.
    * **Planned Entities:** `Workspace`, `Document` (contains status, extraction metadata, hash, workspace_id), `DocumentPage`, `DocumentChunk` (contains text, vector, workspace_id, document_id, index_config).
    * **Stable Identifiers:** UUIDv7 will be used for time-sortable, globally unique, stable identifiers. UUIDv7 guarantees chronological ordering by default in the database.
    * **Tenant Isolation:** A strict multi-tenant scope (`tenant_id`) will be enforced at the ORM layer.
    * **Deletion/Revocation State:** Soft-delete/tombstone flags (e.g., `is_revoked`, `deleted_at`) will be tracked on the `Document` entity. Queries must explicitly filter these out.
    * **Citation Provenance:** Chunks will carry reference to their parent `Document` and `DocumentPage`, allowing generations to cite exact sources.
    * **Explicit Statement:** Phase 1 is **NOT** multi-user secure. The single default scope is a development scaffold, not a security boundary.
    * **Index Configuration:** Embedding configuration (model ID, dimension, revision) will be attached to the index or workspace metadata to ensure query/index embedding mismatches fail clearly.
* **Evidence:**
    * SentinelRAG approved roadmap (Phase 1 vs Phase 2 isolation requirements).
* **Alternatives considered:**
    * **Ignoring scope in Phase 1:** Rejected. Adding `workspace_id` and query filters later requires rewriting every repository query and potentially recreating vector indexes.
    * **Implementing full AuthZ in Phase 1:** Rejected. Violates the strict phasing roadmap.
* **Security consequences:** Preparing the scope parameter now guarantees that Phase 2 only needs to swap the hardcoded "default" scope for an authenticated JWT/Session scope to achieve isolation.
* **Reproducibility consequences:** Stable UUIDv7 identifiers ensure chronological ordering during evaluation artifact generation.
* **Operational consequences:** Requires marginally more verbose repository methods in Phase 1.
* **Revisit conditions:** If PostgreSQL partitioning is required for large multi-tenant instances in Phase 6, the `workspace_id` must be part of the partition key.
