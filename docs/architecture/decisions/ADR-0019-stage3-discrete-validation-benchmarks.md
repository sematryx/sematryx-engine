# ADR-0019: Stage 3 Discrete Validation Benchmarks + Reproducible RNG

## Status

Accepted

## Context

Discrete-only optimization uses stochastic outer sampling; CI tests need stable outcomes without
weakening assertions to probabilistic bands.

## Decision

1. Add `engine/discrete_benchmark_scenarios.py` with tiny **knapsack** and **assignment** penalties
   matching Stage 3 validation goals, plus documented reference optima.
2. Add optional **`rng_seed`** on `optimize()` / `run_optimization()`, forwarded to
   `solve_discrete_baseline` and `solve_hybrid_outer_random_inner_scipy` only (continuous SciPy path
   unchanged aside from unused parameter).
3. Register integration tests and include them in `make benchmark` alongside `tests/performance`.

## Alternatives Considered

- Raise evaluation budgets without seeding (rejected: residual flake risk on slower CI).
- Private test-only hooks into solvers (rejected: harder for external reproducibility).

## Consequences

- Positive: deterministic discrete validation in CI; public reproducibility knob for notebooks.
- Negative: `rng_seed` does not affect SciPy stochastic strategies globally—document scope.
