# ADR-0016: Stage 3 Discrete Solver Baseline

## Status

Accepted

## Context

Stage 3 typed descriptors require an execution path for non-continuous variables without expanding scope to mixed continuous/discrete routing in the same slice.

## Decision

1. Classify descriptor lists as `continuous_only`, `discrete_only`, or `mixed`.
2. **Discrete-only** calls (`integer` and/or `categorical` only) run `solve_discrete_baseline`: uniform random samples over valid assignments, then coordinate neighborhood moves until the evaluation budget is exhausted (deduplicating normalized assignments).
3. **Mixed** calls raise `ValueError` until the hybrid routing slice.
4. Register `discrete_random_neighborhood` as a first-class strategy arm for bandit updates on discrete runs.
5. Preserve `list[float]` objective encoding: integers as float-valued integers; categoricals as float category indices.

## Alternatives Considered

- Route discrete problems through SciPy with rounding (rejected: invalidates guarantees and hides discrete structure).
- Implement generic genetic algorithms first (rejected: heavier slice; baseline random + neighborhood matches PRD).

## Consequences

- Positive: auditable discrete path and tests without SciPy discrete dependence.
- Negative: discrete baseline quality is modest versus specialized MILP/metaheuristics; hybrid routing still required for practical mixed problems.
