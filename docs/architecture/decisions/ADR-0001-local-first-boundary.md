# ADR-0001: Local-First Boundary Enforcement

## Status

Accepted

## Context

The previous Sematryx codebase accumulated coupling to cloud services and platform layers, which made the core engine difficult to maintain and test. The new package must remain local-first by default.

## Decision

The `sematryx-engine` core runtime will not depend on cloud APIs, Neo4j, MCP services, or API-server frameworks in its default execution path.

Enforcement mechanisms:

- forbidden import checks in `scripts/check_forbidden_imports.py`
- policy checks in `scripts/check_policy.py`
- governance docs and templates required in repository structure

## Alternatives Considered

- Keep optional cloud imports in core modules (rejected: boundary erosion risk)
- Soft conventions without scripts (rejected: insufficient enforcement)

## Consequences

- Positive: stable boundaries, faster tests, lower operational complexity
- Negative: adapter work required for optional integrations later
- Follow-up tasks: add CI workflow enforcement and branch protection in GitHub settings

## Amendment (2026-05-07)

Selection policy includes a local-memory deterministic override when a strategy has
at least three domain runs, to reduce cold-start variance and make empirical learning
effects directly testable in integration tests.
