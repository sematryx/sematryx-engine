# ADR-0008: Expand Legacy Continuous Solver Roster (SciPy First)

## Status

Accepted

## Context

Stage 4 requires broader legacy continuous solver parity. Current local engine only exposed three
SciPy strategies.

## Decision

Expand local-first continuous roster with additional SciPy-backed strategies (SHGO and multiple
local `minimize` methods) while keeping a single `solve_with_scipy` entrypoint and no cloud deps.

## Alternatives Considered

- Add non-SciPy optional backends in same slice (rejected: too much risk/scope).
- Keep tiny roster until full parity (rejected: delays measurable Stage 4 progress).

## Consequences

- Positive: larger continuous strategy arm set for selector/bandit learning.
- Negative: some local methods may underperform per problem type and need calibration later.
