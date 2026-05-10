# ADR-0021: Stage 3 Hybrid Outer Refinement (Neighborhood + Staged Inner Budgets)

## Status

Accepted

## Context

`hybrid_outer_random_inner_scipy` used only uniform random discrete outer samples. Mixed
problems often need local moves in discrete space after an initial shell is found, analogous to
the discrete baseline’s neighborhood phase.

## Decision

1. After the random exploration phase, run **coordinate neighborhood refinement** on discrete
   variables: enumerate `discrete_coordinate_neighbors` (same semantics as the discrete baseline)
   from the best discrete assignment found, with inner SciPy solves on each new shell.
2. **Staged inner budgets**: refinement iterations use `inner_budget_refine` (favors larger
   inner budgets when remaining budget allows) vs exploration’s schedule.
3. Expose `discrete_coordinate_neighbors` as a public helper in `discrete_solvers` for reuse.
4. Set `OptimizeResult.message` to `hybrid_outer_random_inner_scipy_refined` to distinguish the
   runtime from the pre-refinement implementation (bandit `strategy_used` remains the composite
   `hybrid_outer_random_inner_scipy` ID).

## Alternatives Considered

- Bayesian / Thompson outer loop (deferred: higher complexity; validate gains on this baseline first).
- Unbounded neighbor enumeration (rejected: cap via budget + seen-set deduplication).

## Consequences

- Positive: better hybrid quality on knapsack-like discrete shells; deterministic with `rng_seed`
  for outer sampling and neighbor order.
- Negative: more inner solves when refinement runs; may consume budget faster on large categorical
  fan-outs (mitigated by global `max_evaluations` and deduplication).
