# ADR-0007: Phase 1 Scope-Aware Data Model

* **Status:** Proposed — pending independent Phase 1A audit
* **Date:** 2026-08-05
* **Context:** SentinelRAG Phase 1 will not implement multi-user authentication or authorization, but the data model must be designed so that Phase 2 can migrate to full tenant isolation without destructive data migrations. Database queries must not depend on a hidden global scope.
* **Decision:**
    * **Single-Workspace Behaviour:** One explicit default workspace in Phase 1.
    * **Explicit Scope-Context Interface:** Scope passed explicitly into repository interfaces. The backend will enforce this context at the query level.
    * **Identifiers:** Application-generated UUIDv4 with PostgreSQL `uuid` storage.
    * **Ordering:** Explicit `created_at` timestamp for ordering.
    * **No secure multi-user claim in Phase 1:** The single default scope is a development scaffold, not a security boundary.
* **Evidence:**
    * SentinelRAG approved roadmap (Phase 1 vs Phase 2 isolation requirements).
* **Alternatives considered:**
    * **Ignoring scope in Phase 1:** Rejected. Adding `workspace_id` and query filters later requires rewriting every repository query and potentially recreating vector indexes.
    * **Implementing full AuthZ in Phase 1:** Rejected. Violates the strict phasing roadmap.
* **Security consequences:** The explicit Phase 1 scope parameter avoids a destructive schema redesign, but it does not provide tenant isolation. Phase 2 must implement authenticated identity, centralized authorization, scoped relational and vector queries, citation authorization, deletion and revocation enforcement, guessed-identifier tests and cross-user canary tests.
    * UUIDv4 does not encode chronological order.
    * Identity does not create isolation by itself.
* **Reproducibility consequences:** Explicit timestamps and UUIDv4 provide traceable provenance.
* **Operational consequences:** Requires marginally more verbose repository methods in Phase 1.
* **Revisit conditions:** If PostgreSQL partitioning is required for large multi-tenant instances in Phase 6, the `workspace_id` must be part of the partition key.
