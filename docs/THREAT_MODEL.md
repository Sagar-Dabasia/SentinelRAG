# Threat Model

## Scope and Current System State
Currently (Phase 0), the system is merely a Python package baseline. This threat model describes the planned system.

## Assets
* Evaluator metrics
* System prompts
* RAG contextual data (Synthetic)

## Threat Actors
* External users/attackers (interacting via the planned API/Dashboard)
* Malicious document providers (indirect injection)

## Trust Boundaries
* API boundary
* Database boundary
* Model provider boundary

## Planned Data Flows
* User Input -> API -> Retrieval -> Model -> API -> Output

## Attack Surfaces
* Chat interface
* Document ingestion pipeline
* Evaluator/metrics dashboard

## Threat Scenarios
* Direct prompt injection (PLANNED)
* Indirect prompt injection (PLANNED)
* Cross-user leakage (PLANNED)
* Retrieval poisoning (PLANNED)
* Sensitive information disclosure (PLANNED)
* System-prompt extraction (PLANNED)
* Broken object-level authorization (PLANNED)
* Unsafe upload (PLANNED)
* MIME spoofing (PLANNED)
* Extension spoofing (PLANNED)
* Path traversal (PLANNED)
* Oversized input (PLANNED)
* Resource exhaustion (PLANNED)
* Malicious document structure (PLANNED)
* Metadata leakage (PLANNED)
* Dependency compromise (PLANNED)
* Secret exposure (PLANNED)
* Log leakage (PLANNED)
* Insecure configuration (PLANNED)
* Model and embedding provenance (PLANNED)
* Evaluation contamination (PLANNED)
* LLM-as-judge bias (PLANNED)

## Planned Controls
* Mitigations for the above threats will be evaluated and implemented in future phases. Currently, all application controls are PLANNED.

## Residual Risks
* LLM hallucinations bypassing mitigations.

## Assumptions
* The environment is completely local and isolated.

## Out-of-Scope Activity
* DDoS protection for public endpoints.
* Hardware-level security.

## Ethical Boundaries
* No testing against real people, proprietary systems, or non-synthetic data.

## Framework Mapping
(Reviewed on 2026-08-05)
* [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
* [OWASP Top 10:2025](https://owasp.org/www-project-top-ten/)
* NIST AI RMF 1.0 (Note: revision work is underway)
* NIST AI 600-1 Generative AI Profile
* [MITRE ATLAS](https://atlas.mitre.org/) (Living knowledge base)

## Review Date
Initial review: 2026-08-05
