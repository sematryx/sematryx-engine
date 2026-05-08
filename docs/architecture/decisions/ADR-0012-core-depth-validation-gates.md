# ADR-0012: Core-Depth Validation Regression Gates

## Status

Accepted

## Context

Stage 4 parity work introduced topology routing, adaptive retries, tuning priors, and explanation
structures. A dedicated integration regression gate is required to prevent drift while remaining
local-first.

## Decision

Add a parity-oriented integration test that validates both benchmark snapshot quality thresholds and
runtime contract completeness (topology + explanation + adaptation + tuned attempt budgets).

## Alternatives Considered

- Rely only on existing narrow integration tests (rejected: does not gate end-to-end parity surfaces).
- Add heavyweight external benchmark harness (rejected: unnecessary for current local CI stage).

## Consequences

- Positive: one gate catches regressions across multiple Stage 4 capabilities.
- Negative: test runtime increases modestly due to benchmark snapshot generation.
