# ADR-0014: Explanation Formatter Helpers

## Status

Accepted

## Context

Structured explanation payloads are comprehensive but cumbersome for direct CLI/notebook consumption.

## Decision

Add first-party formatter helpers returning concise and verbose deterministic summaries from
`OptimizationResult.explanation` metadata.

## Alternatives Considered

- Keep raw dict-only interface (rejected: poor ergonomics for quick inspection).
- Introduce rich renderer dependency (rejected: unnecessary complexity for local-first package).

## Consequences

- Positive: easier debugging/reporting without changing core explanation schema.
- Negative: formatter output must be kept aligned as schema evolves.
