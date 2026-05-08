# ADR-0009: Bounded Autodidactic Retry Loop

## Status

Accepted

## Context

Stage 4 calls for adaptive multi-attempt solving with bounded budgets. Single-shot strategy execution
limits recovery when the first chosen method underperforms.

## Decision

Add a bounded autodidactic loop in optimizer runtime. Attempt count is derived from topology budget
regime (`tight`=1, `moderate`=2, `generous`=3), each attempt gets a split budget, and the best
attempt result is selected and persisted.

## Alternatives Considered

- Unbounded retries (rejected: budget safety risk).
- Retry only on solver failure flag (rejected: misses quality-based improvements).

## Consequences

- Positive: adaptive retries can improve final quality under generous budgets.
- Negative: more solver calls increase runtime for moderate/generous regimes.
