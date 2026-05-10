# ADR-0017: Stage 3 Hybrid Routing for Mixed Descriptors

## Status

Accepted

## Context

Discrete-only and continuous-only paths exist; mixed-variable problems require coordination between discrete assignment search and continuous optimization without breaking the `list[float]` objective contract.

## Decision

1. Encode mixed bounds in descriptor order via `descriptors_to_mixed_encoded_bounds`.
2. Implement **outer random discrete** sampling over discrete dimensions plus **inner SciPy** (or optional non-SciPy continuous arms) on continuous bounds only.
3. Expose composite runtime strategy `hybrid_outer_random_inner_scipy`; bandit rewards update this composite arm (not the inner arm).
4. Extend `StrategySelector.select_with_basis` with `exclude_strategies` so hybrid inner selection cannot pick `discrete_random_neighborhood` or the hybrid composite itself.

## Alternatives Considered

- Single-vector SciPy with rounding on discrete dims (rejected: unstable semantics vs typed descriptors).
- Nested MILP / constraint solver (rejected: scope and dependency risk for this slice).

## Consequences

- Positive: pragmatic mixed problems become runnable with explainable routing.
- Negative: outer loop is random; hard discrete landscapes may need more evaluations or future smarter outer search.
