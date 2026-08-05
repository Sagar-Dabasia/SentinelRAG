# ADR-0002: Local-First Modular Monolith

## Status
Accepted
Date: 2026-08-05

## Context
SentinelRAG requires an architecture that is easy to deploy locally, respects data privacy, and provides a clear boundary for evaluating security controls.

## Decision
We choose a local-first modular monolith architecture.
* We reject microservices, Kubernetes, and complex agent frameworks for the core project to minimize overhead and limit attack surface.
* The system will be divided into distinct modules (API, Dashboard, Database, Model Provider) running locally.
* Security-critical policy will be highly visible within the single codebase rather than dispersed across multiple microservices.

## Consequences
* Simplifies local testing and deployment.
* Limits horizontal scalability (which is a non-goal).
* Requires careful internal modularity to prevent tight coupling.
