# ADR-0018: Stage 3 Discrete Learning Features in Local Memory

## Status

Accepted

## Context

Stage 3 introduces discrete and hybrid solver routes. `LocalStrategyMemory` already stores opaque
`features_json`; continuous-only runs encoded topology-derived `ProblemFeatures` scalars only.

## Decision

1. Add `descriptor_learning_features(descriptors)` producing stable keys:
   `descriptor_mix`, per-kind counts, and `log_discrete_configuration_measure` (sum of natural logs of
   discrete branch counts).
2. On **discrete-only** and **hybrid** optimizer branches, merge these keys plus
   `optimizer_bandit_reward` (same value passed to the bandit update) into the memory payload.
   Hybrid runs additionally store `hybrid_inner_strategy` on the memory row.
3. Expose the descriptor summary unchanged under `explanation.adaptation["descriptor_learning"]` for
   the same routes.

## Alternatives Considered

- New SQLite columns per feature (rejected: JSON payload already carries extensibility).
- Skip memory changes; rely on explanations only (rejected: offline analytics expect SQLite rows).

## Consequences

- Positive: warm-history queries can filter or analyze discrete shapes without replaying runs.
- Negative: payload size grows slightly; consumers must tolerate new optional keys.
