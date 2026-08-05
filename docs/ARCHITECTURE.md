# Architecture

## Current Implemented State (Phase 0)
The current implemented state is purely a repository foundation.
- Python package baseline
- Tooling and dependency lock configuration
- Governance documents

## Planned Components

### Phase 1 Components (PLANNED)
* **Model-provider abstraction:** Interfaces with various underlying LLMs.
* **Ollama adapter:** Local integration for Ollama models.
* **OpenAI-compatible local adapter:** Generic API integration for local endpoints.
* **Embedding service:** Interfaces with the selected embedding models.
* **Basic Document-ingestion service:** Loads files into the system.
* **Parser abstraction:** Standardized interfaces for extracting text from different formats.
* **Deterministic chunking service:** Consistently divides text for embeddings.
* **Retrieval service:** Core logic to query the vector repository.
* **Generation service:** Core logic to prompt the model with context.
* **Citation service:** Links generated text to source chunks.
* **Configuration service:** Manages parameters and feature flags.

### Phase 2 Security Components (PLANNED)
* **Authentication service:** Verifies user identity before any operation.
* **Central authorization policy:** Enforces RBAC/ABAC on all data access.
* **File-validation and quarantine service:** Inspects files (MIME, size, path safety) before parsing.
* **Vector repository:** Stores embeddings (with tenant metadata filtering).
* **Relational metadata repository:** Stores source metadata, users, and permissions.
* **Database-session management:** Safely manages scoped DB connections.
* **Prompt-template registry:** Version-controlled storage of system and user prompts.
* **Audit-event service:** Immutable logging of security-critical actions.

### Phase 3–6 Research Components (PLANNED)
* **Evaluation runner:** Orchestrates tests against the system.
* **Attack-case registry:** Stores standardized prompts for measuring defense utility.
* **Experiment-artifact writer:** Outputs reproducible JSON/JSONL metrics and run conditions.
* **Streamlit research dashboard:** Interface exclusively for running tests and visualizing outcomes (not a production frontend).

### Deferred Phase 7 Deployment Hardening (DEFERRED)
* Containerized deployments
* Kubernetes/compose orchestrations

## Required Security-Critical Placement Invariants
* User identity is established before authorized operations.
* Authorization is server-side.
* Authorization is centralized.
* Tenant filtering occurs within or before retrieval.
* Unauthorized chunks are never sent to the model.
* Citation access uses the same authorization policy.
* Revoked or deleted documents cannot be retrieved.
* User-supplied file paths are never trusted directly.
* Uploaded content and retrieved context are untrusted.
* Model output is untrusted.
* No model-generated code is executed.
* Model providers cannot bypass application authorization.
* Local model service failure must fail safely.
* Prompt templates are versioned.
* Embedding configurations are versioned.
* Index/query embedding mismatches fail clearly.
* Evaluation artifacts record provenance.
* No external paid provider is enabled by default.
* Controlled reduced-defence mode is disabled by default and isolated.

## Required Data Flows

### 1. Authentication
`mermaid
sequenceDiagram
    actor User
    participant Auth as Authentication Service
    User->>Auth: Provide credentials
    Auth-->>User: Issue secure session/token
`
* **Actor:** User
* **Trust-boundary crossings:** API boundary (external to internal)
* **Authorization decision:** N/A (Authentication step)
* **Stored data:** Session token
* **Failure behaviour:** Request denied (401)
* **Provenance recorded:** Audit event of login success/failure

### 2. Document Upload and Validation
`mermaid
sequenceDiagram
    actor User
    participant API as FastAPI Layer
    participant Val as File-validation Service
    participant Store as Quarantine/Storage
    User->>API: Upload document
    API->>Val: Check MIME, size, extension
    Val-->>API: Validated
    API->>Store: Save document
`
* **Actor:** User
* **Trust-boundary crossings:** API boundary, Filesystem boundary
* **Authorization decision:** Validate user can upload to tenant
* **Stored data:** Raw file
* **Failure behaviour:** File rejected (Quarantined or deleted)
* **Provenance recorded:** Upload audit event

### 3. Parsing, Chunking and Embedding
`mermaid
sequenceDiagram
    participant Worker
    participant Parser
    participant Chunker
    participant Embedder
    participant VecStore as Vector Repository
    Worker->>Parser: Extract text
    Parser->>Chunker: Deterministic chunking
    Chunker->>Embedder: Generate embeddings
    Embedder->>VecStore: Store with tenant metadata
`
* **Actor:** System (Background worker)
* **Trust-boundary crossings:** Model provider boundary (Embedding service)
* **Authorization decision:** Implicit (Worker operates on tenant's behalf)
* **Stored data:** Vectors, metadata
* **Failure behaviour:** Job fails, transaction rolled back
* **Provenance recorded:** Embedding model version, document ID

### 4. Authorized Retrieval
`mermaid
sequenceDiagram
    actor User
    participant API
    participant AuthZ as Central Authorization
    participant Ret as Retrieval Service
    participant VecStore as Vector Repository
    User->>API: Search query
    API->>AuthZ: Check read permission
    AuthZ-->>API: Authorized + Tenant ID
    API->>Ret: Search(query, Tenant ID)
    Ret->>VecStore: Filtered similarity search
    VecStore-->>Ret: Chunks
`
* **Actor:** User
* **Trust-boundary crossings:** Database boundary
* **Authorization decision:** Enforce tenant filtering on vector search
* **Stored data:** None
* **Failure behaviour:** Returns 0 results or fails safely
* **Provenance recorded:** Query parameters logged

### 5. Generation and Citation Validation
`mermaid
sequenceDiagram
    actor User
    participant Gen as Generation Service
    participant AuthZ
    participant Model
    User->>Gen: Prompt + Chunks
    Gen->>AuthZ: Validate chunk access
    AuthZ-->>Gen: Authorized
    Gen->>Model: Formatted prompt
    Model-->>Gen: Response
    Gen-->>User: Validated response + citations
`
* **Actor:** User
* **Trust-boundary crossings:** Model provider boundary
* **Authorization decision:** Verify user has access to retrieved chunks before generation
* **Stored data:** None
* **Failure behaviour:** Fallback message or safe failure
* **Provenance recorded:** Model provider, version, parameters

### 6. Document Deletion or Revocation
`mermaid
sequenceDiagram
    actor User
    participant API
    participant AuthZ
    participant DB as Metadata DB
    participant VecStore as Vector Repository
    User->>API: Delete document
    API->>AuthZ: Check delete permission
    AuthZ-->>API: Authorized
    API->>DB: Mark deleted
    API->>VecStore: Remove/tombstone vectors
`
* **Actor:** User
* **Trust-boundary crossings:** Database boundary
* **Authorization decision:** Strict ownership check
* **Stored data:** Tombstone records
* **Failure behaviour:** Transaction rollback
* **Provenance recorded:** Audit event of deletion

### 7. Normal Evaluation Run
`mermaid
sequenceDiagram
    actor Researcher
    participant Runner as Evaluation Runner
    participant Sys as SentinelRAG System
    participant Art as Artifact Writer
    Researcher->>Runner: Start eval (Utility dataset)
    Runner->>Sys: Send queries
    Sys-->>Runner: Responses
    Runner->>Art: Write JSONL
`
* **Actor:** Researcher
* **Trust-boundary crossings:** Internal harness boundary
* **Authorization decision:** Researcher privileges
* **Stored data:** Evaluation metrics
* **Failure behaviour:** Evaluation halted, error logged
* **Provenance recorded:** Git commit, config hash

### 8. Controlled Attack Evaluation
`mermaid
sequenceDiagram
    actor Researcher
    participant Runner
    participant Config
    participant Sys
    Researcher->>Runner: Start attack eval
    Runner->>Config: Check LAB_ONLY enabled
    Config-->>Runner: Confirmed
    Runner->>Sys: Send injection payloads
    Sys-->>Runner: Responses
    Runner->>Art: Record success/failure
`
* **Actor:** Researcher
* **Trust-boundary crossings:** Internal harness boundary
* **Authorization decision:** Requires LAB_ONLY explicit flag
* **Stored data:** Attack outcomes
* **Failure behaviour:** Fail safely if LAB_ONLY missing
* **Provenance recorded:** Dataset manifest digest

### 9. Audit-Event Recording
`mermaid
sequenceDiagram
    participant Component
    participant Audit as Audit Service
    participant DB
    Component->>Audit: Log event (User, Action, Resource)
    Audit->>DB: Immutable append
`
* **Actor:** System components
* **Trust-boundary crossings:** Database boundary
* **Authorization decision:** System level
* **Stored data:** Audit trails
* **Failure behaviour:** Drop or fail-closed based on criticality
* **Provenance recorded:** Timestamp, actor, action

### 10. Experiment-Artifact Generation
`mermaid
sequenceDiagram
    participant Runner
    participant Art as Artifact Writer
    Runner->>Art: Pass metrics, metadata
    Art->>Art: Format JSON/JSONL
    Art->>Filesystem: Write artifact
`
* **Actor:** Evaluation runner
* **Trust-boundary crossings:** Filesystem boundary
* **Authorization decision:** Harness level
* **Stored data:** Experiment JSON/JSONL
* **Failure behaviour:** Output error
* **Provenance recorded:** Random seed, hardware summary, full configuration

## Deployment Model
* **Local modular monolith:** Single deployment unit encapsulating all logic to simplify execution.
* **Separate local model process:** Model inference runs in a distinct process (e.g. Ollama).
* **PostgreSQL/pgvector planned:** Standardized relational and vector storage backend.
* **Streamlit interface:** Provided strictly as a research interface, not as proof of production frontend security.
* **Containers deferred:** Containerization is deferred to Phase 7 until a runnable service exists natively.
* **CPU fallback intent:** Capable of running gracefully on CPU if GPU is absent.
* **Hardware constraints:** Designed to run within RTX 4060 8 GB VRAM limitations.
* **No cloud service requirement:** True local-first architecture ensuring no mandatory external dependencies.
