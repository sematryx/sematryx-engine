# PRD-0022: Stage 3 Hybrid Outer Refinement

## Problem Statement

Uniform random discrete outer sampling alone under-uses the evaluation budget on mixed problems
where the continuous subproblem is easy but the discrete shell must be improved locally.

## Goals

- Add a **refinement phase** after random exploration: discrete coordinate neighbors of the best
  shell, each with an inner continuous solve.
- **Staged inner budgets** so refinement can allocate more SciPy budget per shell when appropriate.
- Public `discrete_coordinate_neighbors` for shared discrete geometry.
- Keep `strategy_used` as `hybrid_outer_random_inner_scipy`; distinguish implementation via
  `OptimizeResult.message` where applicable.

## Non-Goals

- Full Bayesian or acquisition-function outer loop in this slice.
- Changing the hybrid strategy ID in the bandit roster.

## Functional Requirements

- `solve_hybrid_outer_random_inner_scipy` implements exploration + refinement; deduplicates seen
  discrete assignments.
- Unit and integration tests cover a mixed continuous + integer shell with a known optimum.

## Acceptance Criteria (Checklist)

- [x] Refinement phase + staged inner budgets implemented in `hybrid_solvers.py`.
- [x] `discrete_coordinate_neighbors` exported from `discrete_solvers.py`.
- [x] Unit tests (`test_hybrid_solvers`) + integration smoke (`test_stage3_hybrid_outer_refinement`).
- [x] Governance: ADR-0021, VR-0022.

## Verification Link

`docs/process/verification/VR-0022-stage3-hybrid-outer-refinement.md`
