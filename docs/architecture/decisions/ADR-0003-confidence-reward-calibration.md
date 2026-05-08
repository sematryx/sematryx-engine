# ADR-0003: Confidence and Reward Calibration

## Status

Accepted

## Context

Users and benchmarks treat the second return value of `StrategySelector.select` as
confidence. Thompson sampling returned the random draw, which is not a calibrated belief
strength. Domain memory override always returned `0.9`, ignoring evidence depth. Bandit
rewards from `1/(1+best_value)` shrink quickly for large objectives, reducing learning signal
differentiation.

## Decision

1. **Bandit (stochastic):** After sampling arms, return `(chosen_name, posterior_mean(chosen_name))` instead of the draw value.
2. **Memory override:** `confidence = round(min(0.95, 0.72 + 0.06 * usage_count), 10)` for `usage_count >= 3` (exactly three runs yields `0.9`; higher counts increase toward the cap).
3. **Optimizer reward:** `reward = min(1.0, 1.0 / (1.0 + sqrt(max(0.0, best_value))))`.

## Alternatives Considered

- Keep Thompson draw as confidence (rejected: misleading for explainability and reporting).
- Logistic reward on best_value (referred to benchmark evolution slice).

## Consequences

- Positive: confidence aligns with interpretable posteriors; memory reflects evidence strength.
- Negative: downstream consumers of raw Thompson draws must adapt (none in-package).
