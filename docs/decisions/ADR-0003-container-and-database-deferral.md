# ADR-0003: Container and Database Deferral

## Status
Accepted
Date: 2026-08-05

## Context
SentinelRAG will eventually use PostgreSQL with pgvector for local vector search, and containerization for reproducible deployments.

## Decision
We are deferring the implementation of PostgreSQL/pgvector and containerization (Dockerfile/Docker Compose) until a runnable service actually exists in later phases.
Currently, in Phase 0, no application logic exists that requires these tools.

## Consequences
* Phase 0 remains strictly a Python package baseline.
* No overhead from unused databases or containers.
* Migration and reproducibility expectations for later phases will incorporate these technologies when appropriate.
* Hardware and local-development constraints will be evaluated when containers are introduced.
