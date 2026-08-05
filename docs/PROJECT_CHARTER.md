# Project Charter

## Objective
Build a secure, local-first, multi-user RAG research prototype that:
* Uses local model providers
* Safely ingests approved document types
* Produces grounded answers with citations
* Enforces user and document isolation
* Supports controlled red-team evaluation
* Measures security, utility, and performance
* Produces reproducible experiment artifacts
* Maps tested threats and controls to current security frameworks
* Presents results through a research dashboard

## Intended Users
* AI/ML engineers
* Secure-AI researchers
* Academic reviewers
* Portfolio reviewers
* The project maintainer operating the controlled local lab

*(This project does not imply or support public production users.)*

## Scope
* Core local RAG
* Safe ingestion
* Authentication and isolation
* Retrieval authorization
* Direct and indirect prompt injection
* Retrieval poisoning
* Leakage and canary testing
* Evaluation methodology
* Comparative mitigations
* Dashboard
* Automated red-team adapters where justified
* Supply-chain and local deployment hardening

## Non-goals
* No production or enterprise claim
* No paid APIs or required cloud services
* No third-party attack testing
* No real sensitive data (synthetic or public data only)
* No autonomous agents or consequential tools before explicit approval
* No Kubernetes or microservices without measured justification

## Success Criteria
* Reproducible local setup
* Working local RAG
* Correct evidence citations
* Zero maintained cross-user retrieval and canary leakage cases
* Reproducible baseline and defended evaluations
* Measured utility, security, and latency trade-offs
* Traceable experiment metadata
* Honest limitations and failed experiments
* External reviewer can understand and reproduce the work

*(Note: Targets are engineering gates under tested conditions, not proof of universal security.)*
