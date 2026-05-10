# PRD-0023: Stage 3 Discrete Cold→Warm Acceptance + Trend Rows

## Problem Statement

Stage 3 acceptance criterion 3 needed executable proof that local memory warm-up improves discrete-
shaped strategy selection, and operators needed discrete rows in benchmark trend output.

## Goals

- Integrate discrete cold/warm **selection** scenarios into `benchmark_metrics` snapshots.
- Add **objective** rows for knapsack-01 and assignment 2×2 (seeded discrete baseline solves).
- Integration tests dedicated to acceptance (not only bundled snapshot thresholds).
- Markdown trend report lists all scenario/objective keys.

## Non-Goals

- Descriptor-feature keyed memory buckets (remains INTEGRATION_DEBT).

## Acceptance Criteria (Checklist)

- [x] `collect_domain_benchmark_snapshot` exposes `discrete_knapsack` and `discrete_assignment2x2`.
- [x] Objectives include `knapsack01` and `assignment2x2` with near-optimal values.
- [x] Warm vs cold: higher mean confidence and high hit rate on `discrete_random_neighborhood`.
- [x] `test_stage3_discrete_cold_warm_selection` + updated `test_benchmark_metrics_snapshot`.
- [x] ADR-0022 / VR-0023.

## Verification Link

`docs/process/verification/VR-0023-stage3-discrete-cold-warm-acceptance.md`
