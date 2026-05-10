# PRD-0020: Stage 3 Discrete Validation Benchmarks

## Problem Statement

Stage 3 lacked reproducible, CI-gated toy scenarios proving discrete-only optimization reaches
known optima on combinatorial-shaped objectives.

## Goals

- Ship documented **knapsack-shaped** and **assignment-shaped** minimization scenarios with
  reference optima.
- Run them under `tests/integration` (and `make benchmark`) with deterministic discrete/hybrid RNG
  via optional `rng_seed` on `optimize()`.

## Non-Goals

- Full knapsack/scheduling benchmark suites at production scale.
- Extending JSON trend reports in this slice (defer to reporting slice).

## Functional Requirements

- Reusable builders in `engine/discrete_benchmark_scenarios.py`.
- Integration tests assert optimum matching within floating tolerance on seeded runs.

## Acceptance Criteria (Checklist)

- [x] Two scenarios (0/1 knapsack + 2×2 assignment) with documented optimal values.
- [x] Tests pass in CI (`integration-performance`) and are included in `make benchmark`.
- [x] `optimize(..., rng_seed=...)` threads into discrete + hybrid solver RNGs for reproducibility.
- [x] Governance artifacts updated.

## Verification Link

`docs/process/verification/VR-0020-stage3-discrete-validation-benchmarks.md`
