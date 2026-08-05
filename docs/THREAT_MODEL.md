# Threat Model

## Scope and Current System State
Currently (Phase 0), the system is merely a Python package baseline. This threat model describes the planned system architecture and risks using the verified OWASP GenAI LLM Top 10 2026 framework.

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
* **Threat category:** Direct prompt injection, Indirect prompt injection
* **Relevant assets:** Model responses, Extracted text
* **Actor:** Adversarial prompt author, Malicious document author
* **Entry point:** Chat interface, Document ingestion pipeline
* **Attack path:** Attacker submits malicious prompt overrides via chat or document uploads.
* **Impact:** Generation of unauthorized content or unintended behavior.
* **Controls:** Layered mitigations
* **Control status:** PLANNED
* **Residual risk:** LLMs may succumb to novel jailbreaks; delimiters/filters are incomplete solutions.
* **Implementation phase:** Phase 5
* **Testing phase:** Phase 4
* **Framework mapping:** LLM01:2026 — Prompt Injection
* **Mapping rationale:** Manipulating LLM input to alter intent fits prompt injection.

### TR-02: Hidden Context Exposure & Extraction
* **Threat ID:** TR-02
* **Threat category:** System-prompt extraction, Hidden-context exposure
* **Relevant assets:** System prompts, Application configuration
* **Actor:** Adversarial prompt author
* **Entry point:** Chat interface
* **Attack path:** Attacker injects prompts to extract hidden instructions, private reasoning, or internal application state.
* **Impact:** Disclosure of system instructions and contextual state.
* **Controls:** Layered mitigations
* **Control status:** PLANNED
* **Residual risk:** Prompt leakage via advanced extraction attacks.
* **Implementation phase:** Phase 5
* **Testing phase:** Phase 4
* **Framework mapping:** LLM08:2026 — Hidden Context Exposure (and LLM01:2026 — Prompt Injection)
* **Mapping rationale:** Exposure of system instructions or private context maps to LLM08; when attempted via injection, it also maps to LLM01.

### TR-03: Cross-User Leakage & Access Control
* **Threat ID:** TR-03
* **Threat category:** Cross-user or cross-tenant leakage, Improper access control, Broken object-level authorization
* **Relevant assets:** User accounts, Uploaded documents
* **Actor:** Malicious authenticated user, Unauthenticated attacker
* **Entry point:** API endpoints
* **Attack path:** Attacker exploits broken object-level authorization to access or leak other users' data.
* **Impact:** Cross-user data breach.
* **Controls:** Authentication, Authorization, Cross-user isolation
* **Control status:** PLANNED
* **Residual risk:** Implementation bugs in authorization logic.
* **Implementation phase:** Phase 2
* **Testing phase:** Phase 2
* **Framework mapping:** Conventional Authorization (OWASP API1:2023)
* **Mapping rationale:** LLM vulnerabilities do not replace the need for conventional server-side authorization.

### TR-04: Sensitive Information Disclosure
* **Threat ID:** TR-04
* **Threat category:** Sensitive information disclosure
* **Relevant assets:** Model responses, Uploaded documents
* **Actor:** Malicious authenticated user, Adversarial prompt author
* **Entry point:** Chat interface
* **Attack path:** LLM inappropriately discloses sensitive data contained within its legitimate retrieval context.
* **Impact:** Sensitive information leakage.
* **Controls:** Layered mitigations, Retrieval filtering, Citation authorization
* **Control status:** PLANNED
* **Residual risk:** The model failing to respect confidentiality constraints.
* **Implementation phase:** Phase 5
* **Testing phase:** Phase 4
* **Framework mapping:** LLM02:2026 — Sensitive Information Disclosure
* **Mapping rationale:** The model inappropriately outputs sensitive data it was given access to.

### TR-05: Excessive Agency
* **Threat ID:** TR-05
* **Threat category:** Excessive model or tool permissions
* **Relevant assets:** Internal APIs, Local model service
* **Actor:** Adversarial prompt author
* **Entry point:** Chat interface
* **Attack path:** LLM autonomously executes unauthorized operations using provided tools.
* **Impact:** Unauthorized actions or resource mutation.
* **Controls:** None currently applicable; SentinelRAG has no tools or autonomous agents.
* **Control status:** DEFERRED — extend the threat model before tool introduction
* **Residual risk:** Unforeseen model autonomy.
* **Implementation phase:** DEFERRED
* **Testing phase:** DEFERRED
* **Framework mapping:** LLM03:2026 — Excessive Agency
* **Mapping rationale:** Granting LLMs unchecked autonomy maps to excessive agency.

### TR-06: Foundation Supply Chain & Configuration
* **Threat ID:** TR-06
* **Threat category:** Dependency compromise, Secret exposure, Insecure default configuration
* **Relevant assets:** Source code, Build and CI workflow
* **Actor:** Compromised dependency, Careless developer
* **Entry point:** GitHub repository, CI
* **Attack path:** Attacker compromises build dependencies or developer commits secrets/insecure defaults.
* **Impact:** Codebase compromise, secret exposure.
* **Controls:** Dependency lock, CI dependency audit, Secret scanning, Pinned actions, Governance documentation
* **Control status:** IMPLEMENTED and TESTED
* **Residual risk:** Zero-days in trusted tools.
* **Implementation phase:** Phase 0
* **Testing phase:** Phase 0
* **Framework mapping:** LLM04:2026 — Supply Chain
* **Mapping rationale:** Affects foundational dependencies and configuration.

### TR-07: Advanced Supply Chain & Runtime Risks
* **Threat ID:** TR-07
* **Threat category:** Dependency compromise, Log leakage, Insecure default configuration
* **Relevant assets:** Container images, Runtime environment
* **Actor:** Compromised dependency, Misconfigured administrator
* **Entry point:** Container boundary, Runtime
* **Attack path:** Compromised container base image, vulnerable SBOM packages, or leaked logs in production.
* **Impact:** Runtime compromise.
* **Controls:** Containers, SBOM, Container scanning, Runtime privilege reduction, Advanced supply-chain hardening
* **Control status:** PLANNED
* **Residual risk:** Undetected supply chain attacks in production.
* **Implementation phase:** Phase 7
* **Testing phase:** Phase 7
* **Framework mapping:** LLM04:2026 — Supply Chain
* **Mapping rationale:** Production-level supply chain and runtime risks.

### TR-08: Retrieval Poisoning
* **Threat ID:** TR-08
* **Threat category:** Retrieval poisoning
* **Relevant assets:** Uploaded documents, Vector indexes
* **Actor:** Malicious document author
* **Entry point:** Document ingestion pipeline
* **Attack path:** Attacker uploads malicious content to corrupt retrieval context.
* **Impact:** Compromised LLM responses due to poisoned context.
* **Controls:** Retrieval filtering, Layered mitigations
* **Control status:** PLANNED
* **Residual risk:** Subtle malicious data evades filters.
* **Implementation phase:** Phase 5
* **Testing phase:** Phase 4
* **Framework mapping:** LLM05:2026 — Data and Model Poisoning
* **Mapping rationale:** Manipulating the data corpus to poison retrieval mappings.

### TR-09: Unbounded Consumption
* **Threat ID:** TR-09
* **Threat category:** Unbounded query consumption, Resource exhaustion
* **Relevant assets:** Local model service, API endpoints
* **Actor:** Unauthenticated attacker, Malicious authenticated user
* **Entry point:** API endpoints
* **Attack path:** Attacker sends unbounded queries or excessive inference requests (denial-of-wallet).
* **Impact:** Denial of service, resource exhaustion.
* **Controls:** Resource-abuse attack cases, Layered mitigations
* **Control status:** PLANNED
* **Residual risk:** Application-level DoS.
* **Implementation phase:** Phase 5
* **Testing phase:** Phase 4
* **Framework mapping:** LLM06:2026 — Unbounded Consumption
* **Mapping rationale:** Exhausting model inference resources maps directly to Unbounded Consumption.

### TR-10: Ingestion File Risks
* **Threat ID:** TR-10
* **Threat category:** Unsafe file upload, MIME-type spoofing, File-extension spoofing, Path traversal, Oversized files, Malicious document structure
* **Relevant assets:** Uploaded documents, Host filesystem
* **Actor:** Malicious document author
* **Entry point:** Ingestion pipeline
* **Attack path:** Attacker uploads oversized or malformed files to trigger path traversal or parsing bugs.
* **Impact:** RCE, filesystem compromise, denial of service.
* **Controls:** Secure ingestion, MIME and extension checks, Path safety, File-size and extraction limits, Oversized-file negative tests
* **Control status:** PLANNED
* **Residual risk:** Zero-day in parsing library.
* **Implementation phase:** Phase 2
* **Testing phase:** Phase 2
* **Framework mapping:** Conventional ingestion and resource validation
* **Mapping rationale:** Oversized and unsafe files are conventional ingestion and validation issues.

### TR-11: Misinformation
* **Threat ID:** TR-11
* **Threat category:** Misinformation or unsupported model output
* **Relevant assets:** Model responses
* **Actor:** Normal authenticated user
* **Entry point:** Chat interface
* **Attack path:** Model naturally hallucinates, outputs misleading information, or provides unsupported answers.
* **Impact:** User relies on incorrect information.
* **Controls:** Citations, Comparative defence experiments, Utility and latency trade-offs
* **Control status:** PLANNED
* **Residual risk:** Inherent LLM hallucination rates.
* **Implementation phase:** Phase 5
* **Testing phase:** Phase 5
* **Framework mapping:** LLM07:2026 — Misinformation
* **Mapping rationale:** Unsupported, hallucinated, or misleading model answers.

### TR-12: Vector & Embedding Weaknesses
* **Threat ID:** TR-12
* **Threat category:** Vector-store metadata leakage
* **Relevant assets:** Vector indexes, Metadata
* **Actor:** Malicious authenticated user
* **Entry point:** API endpoints
* **Attack path:** Attacker extracts metadata from the vector store belonging to other tenants.
* **Impact:** Sensitive information disclosure.
* **Controls:** Vector metadata isolation
* **Control status:** PLANNED
* **Residual risk:** Misconfigured vector indexes.
* **Implementation phase:** Phase 2
* **Testing phase:** Phase 2
* **Framework mapping:** LLM09:2026 — Vector and Embedding Weaknesses
* **Mapping rationale:** Leakage or weaknesses specific to vector stores map to LLM09, but this does not substitute for access-control testing.

### TR-13: Insecure Output Handling
* **Threat ID:** TR-13
* **Threat category:** Insecure output handling
* **Relevant assets:** Model responses, Browser/dashboard
* **Actor:** Malicious document author
* **Entry point:** API boundary
* **Attack path:** Malicious output is rendered insecurely, causing XSS or downstream execution.
* **Impact:** XSS, arbitrary downstream execution.
* **Controls:** Basic output handling
* **Control status:** PLANNED
* **Residual risk:** Evasion of output sanitization.
* **Implementation phase:** Phase 1
* **Testing phase:** Phase 1
* **Framework mapping:** LLM10:2026 — Improper Output Handling
* **Mapping rationale:** Unsafe rendering or execution of model output.

### TR-14: Model Provenance Risk
* **Threat ID:** TR-14
* **Threat category:** Model or embedding provenance risk
* **Relevant assets:** Local model service, Embeddings
* **Actor:** Compromised dependency
* **Entry point:** Model provider boundary
* **Attack path:** Tainted models are downloaded or used without provenance verification.
* **Impact:** Compromised model integrity.
* **Controls:** Model and embedding provenance recording
* **Control status:** PLANNED
* **Residual risk:** Upstream compromise of trusted models.
* **Implementation phase:** Phase 1
* **Testing phase:** Phase 1
* **Framework mapping:** LLM04:2026 — Supply Chain
* **Mapping rationale:** Compromised models, embedding models, or datasets map to Supply Chain risks.

### TR-15: Evaluation Integrity
* **Threat ID:** TR-15
* **Threat category:** Evaluation-data contamination, LLM-as-judge bias
* **Relevant assets:** Evaluator metrics, Evaluation results
* **Actor:** Normal authenticated user
* **Entry point:** Red-team harness
* **Attack path:** Evaluation datasets overlap with training data, or LLM judges exhibit systemic bias.
* **Impact:** Overestimation of safety, compromised metrics.
* **Controls:** Dataset manifests, Evaluation contamination controls, Deterministic metrics, LLM-judge calibration and bias analysis, Reproducible experiment metadata
* **Control status:** PLANNED
* **Residual risk:** Inherent bias in LLM evaluators.
* **Implementation phase:** Phase 3
* **Testing phase:** Phase 3
* **Framework mapping:** LLM05:2026 — Data and Model Poisoning (and conventional research validity)
* **Mapping rationale:** Accidental evaluation contamination is a research-validity risk and data poisoning concern.

## Assumptions
* The environment is completely local and isolated.

## Ethical Boundaries
* No testing against real people, proprietary systems, or non-synthetic data.

## Framework Mapping
(Framework facts supplied by independent repository auditor on 2026-08-05)
* [OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) (Released 2026-08-03)
* Official companion repository: [GenAI-LLM-Top10](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10)
* [OWASP Top 10:2025](https://owasp.org/www-project-top-ten/)
* NIST AI RMF 1.0
* NIST AI 600-1 Generative AI Profile
* [MITRE ATLAS](https://atlas.mitre.org/)
