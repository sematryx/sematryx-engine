# ADR-0007: Explanation Schema Contract on OptimizationResult

## Status

Accepted

## Context

Stage 2 explainability follow-up requires stable, auditable rationale data. Existing results did not
carry structured selection basis metadata.

## Decision

Add an optional `explanation` payload on `OptimizationResult`. Populate it in the optimizer with:
selection basis, confidence, strategy, domain, and topology tunneling evidence.

## Alternatives Considered

- Free-form explanation string only (rejected: hard to validate and evolve).
- Separate side-channel logs (rejected: weak API ergonomics for users/tests).

## Consequences

- Positive: deterministic contract for explainability tests and downstream formatting.
- Negative: API payload grows and must remain versioned via docs/tests.
