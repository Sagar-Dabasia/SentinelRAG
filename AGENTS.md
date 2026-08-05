# Agent Policy

This document defines the rules and governance framework for AI coding assistants working in this repository.

## Repository Purpose
SentinelRAG is a research prototype and portfolio project investigating RAG security vulnerabilities and mitigations using a local-first modular monolith architecture.

## Current Phase
Phase 0 is complete.
**Phase 1 — Core local RAG baseline** is next.

Phase 1 implementation has not started. The current implemented state remains the minimal package, governance, and tooling foundation. Planned components must not be described as implemented.

## Architecture Summary
Phase 0 contains only repository governance, tooling, and the minimal package baseline. FastAPI, PostgreSQL/pgvector, Streamlit, and local model integration are the approved **planned architecture**. Agents must inspect the repository before assuming any planned component exists.

## Security Invariants
* User identity is established before authorized operations.
* Authorization is server-side and centralized.
* Tenant filtering occurs within or before retrieval.
* Unauthorized chunks are never sent to the model.
* Citation access uses the same authorization policy.
* Revoked or deleted documents cannot be retrieved.
* User-supplied file paths are never trusted directly.
* Uploaded content, retrieved context, and model output are untrusted.
* No model-generated code is executed.
* Model providers cannot bypass application authorization.
* Local model service failure must fail safely.
* Prompt templates and embedding configurations are versioned.
* Index/query embedding mismatches fail clearly.
* Evaluation artifacts record provenance.
* No external paid provider is enabled by default.
* Controlled reduced-defence mode is disabled by default and isolated.


## Architecture & Security Verification
* Architecture and roadmap documents must be checked before assigning components to phases.
* Planned components must never be described in present tense as implemented.
* Security decisions may not be described as implicit.
* Authorization context must be explicit and testable.
* Phase-status and phase-report documents must be updated in every authorized phase-closing task.

## Data Restrictions
* No real personal records, confidential employer or customer data, or real tenant secrets may be used. Synthetic or public data only.
* Completely local environment only. No public endpoints.

## Testing Requirements
* Tests must be runnable offline.
* Coverage must be maintained.
* Security invariants must be explicitly asserted in tests.

## Documentation Requirements
* Documentation must reflect the actual implementation state honestly.
* No future component may be described as implemented.

## Evidence Hierarchy
1. GitHub proves remote state, not local working-tree cleanliness.
2. Local cleanliness must be supported by exact `git status --short` output.
3. Repository files and executed command outputs outrank agent assumptions.
4. No command output or test result may be fabricated.

## Repository-First Workflow & Expected Checks
* Always verify the starting state first by checking branch and commit hashes (`git remote -v`, `git branch --show-current`, `git rev-parse HEAD`, `git fetch origin`, `git rev-parse origin/main`).
* If the starting state mismatches expectations, STOP immediately. Preserve partial work when blocked.

## Focused-Change Policy
* Only modify files explicitly within the scope of the approved prompt.
* No unrelated cleanup.
* No future-phase implementation.
* No deletion of historical or failed evidence.

## Commit and Push Workflow
* Coding agents may commit and push ONLY when the current approved prompt explicitly authorizes it.
* The standing project workflow expects authorized tasks to make **exactly one focused commit** per approved task.
* **Normal push only** (`git push origin main`).
* **NO** force push.
* **NO** amend.
* **NO** rebase.
* **NO** history rewriting.
* **NO** destructive reset.

## Exact Return Fields
Upon successfully pushing an authorized commit, return ONLY:
```text
Commit hash: <full 40-character hash>
Push verified: YES
```

If the task is blocked for any reason (state mismatch, test failure, etc.), return ONLY:
```text
BLOCKED
Reason: <exact blocker>
Commit performed: NO
Push performed: NO
```

## Remote Audit Requirement
All Phase completions and major governance updates require an independent remote audit. Progress is not awarded locally until the remote audit confirms success.
