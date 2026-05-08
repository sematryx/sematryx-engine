# ADR-0015: Stage 3 Typed Variable Descriptors Kickoff

## Status

Accepted

## Context

Stage 3 begins with typed variable descriptors (`continuous`, `integer`, `categorical`) but discrete
solvers are not yet integrated.

## Decision

Add descriptor parsing/validation in API now. Continuous descriptors map to bounds and run through
existing continuous pipeline; integer/categorical descriptors are validated then rejected with clear
Stage-3-kickoff error until solver baseline slice lands.

## Alternatives Considered

- Delay descriptor schema until discrete solver implementation (rejected: blocks early contract validation).
- Silently coerce integer/categorical descriptors to continuous (rejected: misleading behaviour).

## Consequences

- Positive: typed API contract can be tested/documented immediately.
- Negative: users receive explicit errors for non-continuous descriptors until next slices.
