# Threat Model

## Scope and Current System State
Currently (Phase 0), the system is merely a Python package baseline. This threat model describes the planned system architecture and risks.

## Assets
* User accounts
* Authentication state
* Uploaded documents
* Extracted text
* Embeddings
* Vector indexes
* Metadata
* System prompts
* Application configuration
* Audit records
* Model responses
* Evaluation results
* API endpoints
* Local model endpoint
* Database credentials
* Container images
* Source code
* Build and CI workflow

## Trust Boundaries
* Browser/dashboard
* FastAPI backend
* Ingestion pipeline
* Relational database
* Vector storage
* Local model service
* Red-team harness
* CI
* Host filesystem
* Container boundary
* GitHub repository

## Threat Actors
* Normal authenticated user
* Malicious authenticated user
* Unauthenticated attacker
* Malicious document author
* Compromised dependency
* Careless developer
* Misconfigured administrator
* Adversarial prompt author

## Threat Analysis

### TR-01: Direct Prompt Injection
* **Threat ID:** TR-01
* **Relevant asset:** Model responses, API endpoints
* **Actor:** Malicious authenticated user, Adversarial prompt author
* **Entry point:** Chat interface input
* **Attack path:** User submits malicious prompt overrides via chat, bypassing system instructions.
* **Impact:** Generation of unauthorized content or extraction of internal instructions.
* **Planned control:** PLANNED - Input validation, guardrails, and system prompt hardening.
* **Current status:** PLANNED
* **Residual risk:** LLMs may still hallucinate or be tricked by novel jailbreaks.
* **Planned testing phase:** Phase 2 (Red Teaming)
* **Framework mapping:** OWASP LLM01:2025

### TR-02: Indirect Prompt Injection
* **Threat ID:** TR-02
* **Relevant asset:** Model responses, Extracted text, Uploaded documents
* **Actor:** Malicious document author
* **Entry point:** Document ingestion pipeline
* **Attack path:** Attacker uploads a document containing malicious instructions that are ingested and later retrieved into the context window.
* **Impact:** The LLM executes instructions planted in the uploaded document during retrieval.
* **Planned control:** PLANNED - Strict parsing, data sanitization, and separation of instructions from context.
* **Current status:** PLANNED
* **Residual risk:** Complex payloads in obscure file formats may evade sanitization.
* **Planned testing phase:** Phase 2 (Red Teaming)
* **Framework mapping:** OWASP LLM01:2025

### TR-03: Sensitive Information Disclosure
* **Threat ID:** TR-03
* **Relevant asset:** Uploaded documents, Metadata, Database credentials
* **Actor:** Malicious authenticated user, Unauthenticated attacker
* **Entry point:** API endpoints, Database boundary
* **Attack path:** Attacker exploits broken object-level authorization to access documents they do not own.
* **Impact:** Leakage of sensitive context or credentials.
* **Planned control:** PLANNED - Robust RBAC, object-level authorization checks, and secure secret management.
* **Current status:** PLANNED
* **Residual risk:** Misconfiguration in deployment environments.
* **Planned testing phase:** Phase 1 (Application build)
* **Framework mapping:** OWASP API1:2023

### TR-04: Supply Chain Compromise
* **Threat ID:** TR-04
* **Relevant asset:** Source code, Build and CI workflow, Container images
* **Actor:** Compromised dependency
* **Entry point:** GitHub repository, CI
* **Attack path:** A third-party dependency is compromised and executes malicious code during build or runtime.
* **Impact:** Full system compromise, secret leakage.
* **Planned control:** PLANNED - Strict lockfile management, dependency auditing, and least-privilege CI.
* **Current status:** PLANNED (Initial CI setup implemented, but application dependencies deferred).
* **Residual risk:** Zero-day vulnerabilities in heavily relied-upon packages.
* **Planned testing phase:** Phase 0 / Phase 1
* **Framework mapping:** OWASP LLM05:2025

## Assumptions
* The environment is completely local and isolated.

## Ethical Boundaries
* No testing against real people, proprietary systems, or non-synthetic data.

## Framework Mapping
(Reviewed on 2026-08-05)
* [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
* [OWASP Top 10:2025](https://owasp.org/www-project-top-ten/)
* NIST AI RMF 1.0 (Note: revision work is underway)
* NIST AI 600-1 Generative AI Profile
* [MITRE ATLAS](https://atlas.mitre.org/) (Living knowledge base)
