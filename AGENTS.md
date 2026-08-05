# Agent Policy

This document defines the rules for AI coding assistants working in this repository.

## Repository Purpose
SentinelRAG is a research prototype and portfolio project investigating RAG security vulnerabilities and mitigations.

## Current Phase
We are currently in Phase 0: Repository and governance foundation.

## Current Architecture Status
Only a minimal Python package and development tooling exist. No application, API, database, or UI is implemented yet.

## Invariants
* **Local-first requirement**: Must be capable of running locally without cloud services.
* **Free/open-source requirement**: All tools, dependencies, and models must be free and open-source.
* **Data restrictions**: No real personal records, confidential employer or customer data, or real tenant secrets may be used. Synthetic or public data only.
* **Security invariants**: No network call during package import/tests. No secrets or credentials. No insecure configuration by default.
* **Testing requirements**: Tests must be runnable offline. Coverage must be maintained.
* **Documentation requirements**: Documentation must reflect the actual implementation state honestly.
* **Evidence requirements**: No command output or test result may be fabricated.

## Git and Branch Policy
* Feature work should be done in scoped branches (when in later phases).
* No destructive Git operations are permitted.

## Coding Agent Constraints
* **No commit or push** without explicit user authorization.
* **No fabricated command output**. Use real tool results.
* **No false completion claim**. State exactly what was done and what remains.
* **No implementation of future phases** without an approved prompt. (Do not build FastAPI, PostgreSQL, etc. in Phase 0).
* **No deletion of failed or historical evidence** by default.
* **Required return fields** after each task as requested by the user.
* **Requirement to stop on repository-state mismatch**. Do not proceed if the repository state differs from instructions.

Repository files and executed commands outrank agent assumptions.
