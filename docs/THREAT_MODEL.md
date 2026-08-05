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
* Evaluator metrics
* RAG contextual data (Synthetic)

## Trust Boundaries
* API boundary
* Database boundary
* Model provider boundary
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
* External users/attackers (interacting via the planned API/Dashboard)
* Malicious document providers (indirect injection)
* Normal authenticated user
* Malicious authenticated user
* Unauthenticated attacker
* Malicious document author
* Compromised dependency
* Careless developer
* Misconfigured administrator
* Adversarial prompt author

## Threat Analysis

### TR-01: Direct & Indirect Prompt Injection
* **Threat ID:** TR-01
* **Threat category:** Prompt Injection (Direct prompt injection, Indirect prompt injection, System-prompt extraction)
* **Relevant assets:** Model responses, Extracted text, System prompts, API endpoints
* **Actor:** Adversarial prompt author, Malicious document author
* **Entry point:** Chat interface input, Document ingestion pipeline
* **Attack path:** Attacker submits malicious prompt overrides via chat or document uploads, extracting system prompts or altering output.
* **Impact:** Generation of unauthorized content or internal instruction leakage.
* **Planned controls:** PLANNED - Input validation, guardrails, and system prompt hardening.
* **Current status:** PLANNED
* **Residual risk:** LLMs may hallucinate or succumb to novel jailbreaks.
* **Planned implementation phase:** Phase 5 (Layered defences and comparative experiments)
* **Planned testing phase:** Phase 4 (Controlled red-team baseline)
* **Framework mapping:** OWASP LLM01:2025

### TR-02: Retrieval Poisoning & Output Handling
* **Threat ID:** TR-02
* **Threat category:** Data Poisoning & Output Risks (Retrieval poisoning, Insecure output handling)
* **Relevant assets:** Uploaded documents, Extracted text, Model responses
* **Actor:** Malicious document author, Malicious authenticated user
* **Entry point:** Document ingestion pipeline, API boundary
* **Attack path:** Attacker introduces malicious data into the vector store. Downstream components render insecure output.
* **Impact:** XSS on dashboard, corrupted context, misinformed responses.
* **Planned controls:** PLANNED - Output encoding, secure parsing, and retrieval auditing.
* **Current status:** PLANNED
* **Residual risk:** Complex outputs or markdown rendering may evade filters.
* **Planned implementation phase:** Phase 5
* **Planned testing phase:** Phase 4
* **Framework mapping:** OWASP LLM02:2025, LLM03:2025

### TR-03: Access Control & Data Leakage
* **Threat ID:** TR-03
* **Threat category:** Access Control (Cross-user or cross-tenant leakage, Sensitive information disclosure, Improper access control, Broken object-level authorization)
* **Relevant assets:** User accounts, Uploaded documents, Vector indexes, Metadata
* **Actor:** Malicious authenticated user, Unauthenticated attacker
* **Entry point:** API endpoints, Database boundary
* **Attack path:** Attacker exploits broken object-level authorization to access or leak other users' documents.
* **Impact:** Data breach, sensitive information disclosure.
* **Planned controls:** PLANNED - Robust RBAC, object-level authorization checks.
* **Current status:** PLANNED
* **Residual risk:** Deployment misconfigurations.
* **Planned implementation phase:** Phase 2 (Identity, isolation and secure ingestion)
* **Planned testing phase:** Phase 2
* **Framework mapping:** OWASP API1:2023, LLM06:2025

### TR-04: Ingestion & File Processing Risks
* **Threat ID:** TR-04
* **Threat category:** File Upload Vulnerabilities (Unsafe file upload, MIME-type spoofing, File-extension spoofing, Path traversal, Malicious document structure)
* **Relevant assets:** Uploaded documents, Host filesystem
* **Actor:** Malicious document author
* **Entry point:** Ingestion pipeline
* **Attack path:** Attacker uploads malformed files or spoofed extensions to trigger path traversal or exploit parser vulnerabilities.
* **Impact:** RCE on ingestion workers, filesystem compromise.
* **Planned controls:** PLANNED - Strict MIME/extension validation, sandboxed parsing, path sanitization.
* **Current status:** PLANNED
* **Residual risk:** Zero-day vulnerabilities in document parsing libraries.
* **Planned implementation phase:** Phase 2
* **Planned testing phase:** Phase 2
* **Framework mapping:** OWASP Top 10:2025 A04 (Insecure Design)

### TR-05: Denial of Service & Resource Exhaustion
* **Threat ID:** TR-05
* **Threat category:** Availability (Oversized files, Resource exhaustion, Unbounded query consumption)
* **Relevant assets:** Local model service, API endpoints
* **Actor:** Unauthenticated attacker, Malicious authenticated user
* **Entry point:** API endpoints, Ingestion pipeline
* **Attack path:** Attacker uploads oversized files or sends unbounded queries to exhaust memory/compute.
* **Impact:** Denial of service, system crash.
* **Planned controls:** PLANNED - Rate limiting, file size limits, query depth bounds.
* **Current status:** PLANNED
* **Residual risk:** Application-level DoS might still occur before rate limits kick in.
* **Planned implementation phase:** Phase 7 (Supply-chain and deployment hardening)
* **Planned testing phase:** Phase 6 (Automated red teaming and dashboard)
* **Framework mapping:** OWASP API4:2023

### TR-06: Supply Chain & Infrastructure Risks
* **Threat ID:** TR-06
* **Threat category:** Infrastructure (Dependency compromise, Secret exposure, Log leakage, Insecure default configuration)
* **Relevant assets:** Source code, Build and CI workflow, Container images, Audit records
* **Actor:** Compromised dependency, Careless developer, Misconfigured administrator
* **Entry point:** GitHub repository, CI, Container boundary
* **Attack path:** Third-party dependency is compromised, or misconfigurations leak secrets/logs.
* **Impact:** Full system compromise, unauthorized access.
* **Planned controls:** PLANNED - Lockfile management, secret scanning, secure defaults, sanitized logging.
* **Current status:** PLANNED
* **Residual risk:** Zero-day vulnerabilities in heavily relied-upon packages.
* **Planned implementation phase:** Phase 7
* **Planned testing phase:** Phase 7
* **Framework mapping:** OWASP LLM05:2025, OWASP Top 10:2025 A05, A06

### TR-07: Evaluation & Model Integrity
* **Threat ID:** TR-07
* **Threat category:** AI Integrity (Model or embedding provenance risk, Evaluation-data contamination, LLM-as-judge bias, Excessive model or tool permissions, Vector-store metadata leakage)
* **Relevant assets:** Evaluator metrics, Evaluation results, Model responses
* **Actor:** Adversarial prompt author, Compromised dependency
* **Entry point:** Red-team harness, Model provider boundary
* **Attack path:** Tainted models, biased judges, or evaluation data overlap leads to false security confidence or excessive tool use.
* **Impact:** Overestimation of safety, compromised model integrity, metadata leakage.
* **Planned controls:** PLANNED - Strict train/test separation, provenance tracking, deterministic evaluation checks, least-privilege tool access.
* **Current status:** PLANNED
* **Residual risk:** Inherent bias in LLM evaluators.
* **Planned implementation phase:** Phase 3 (Reproducible evaluation framework)
* **Planned testing phase:** Phase 3
* **Framework mapping:** OWASP LLM08:2025, LLM10:2025

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
