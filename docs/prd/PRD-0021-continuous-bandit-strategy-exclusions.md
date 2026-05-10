# PRD-0021: Continuous Path Bandit Exclusions

## Problem Statement

Bounds-only optimization must never dispatch discrete-only or hybrid outer strategies,
which require variable descriptors and different solver wiring.

## Goals

- Guard continuous `run_optimization` so the bandit cannot select `discrete_random_neighborhood`
  or `hybrid_outer_random_inner_scipy`.
- Add a regression integration test and document the behavior.

## Non-Goals

- Changing hybrid or discrete-specific selection logic beyond the continuous entry path.

## Functional Requirements

- `exclude_strategies` on `select_with_basis` for the continuous branch of `run_optimization`.
- Integration assertion on `strategy_used` for a representative bounds-only run.

## Acceptance Criteria (Checklist)

- [x] Continuous path passes `exclude_strategies` including both discrete and hybrid arms.
- [x] New integration test fails on the pre-fix behavior (hybrid arm reachable) and passes after the guard.
- [x] Governance artifacts (ADR-0020, VR-0021) and policy gates satisfied.

## Verification Link

`docs/process/verification/VR-0021-continuous-bandit-strategy-exclusions.md`
