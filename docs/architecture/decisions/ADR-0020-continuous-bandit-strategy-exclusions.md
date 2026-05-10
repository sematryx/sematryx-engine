# ADR-0020: Exclude Discrete/Hybrid Arms From Continuous Bounds-Only Selection

## Status

Accepted

## Context

The contextual bandit roster includes `discrete_random_neighborhood` and
`hybrid_outer_random_inner_scipy`. Those strategies require descriptor-shaped
Optimizer paths and dedicated dispatch; bounds-only continuous runs route through
`solve_with_strategy`, which cannot execute hybrid outer loops.

On fresh CI environments (empty bandit/memory prior), the bandit could select a
hybrid arm for a pure continuous problem, causing `ValueError` in non-SciPy dispatch.

## Decision

For bounds-only `run_optimization`, pass `exclude_strategies=frozenset({
"discrete_random_neighborhood", "hybrid_outer_random_inner_scipy"})` into
`StrategySelector.select_with_basis`, mirroring the exclusion already applied when
choosing the inner continuous strategy for hybrid problems.

## Alternatives Considered

- Teach `solve_with_strategy` to branch hybrid/discrete (rejected: duplicates hybrid encoding logic).
- Remove hybrid/discrete from global `STRATEGIES` (rejected: breaks hybrid/discrete paths that legitimately update the bandit).

## Consequences

- Positive: deterministic safe routing for continuous-only calls; CI integration suite stable on cold bandit state.
- Negative: memory recommendations that name hybrid/discrete for a continuous-shaped problem are ignored when excluded (expected).
