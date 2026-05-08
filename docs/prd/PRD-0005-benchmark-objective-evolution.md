# PRD: Benchmark Objective Evolution

## Problem Statement

Selection-only benchmarks do not validate end-to-end objective quality after solver execution.

## Goals

- Add isolated sphere objective runs with recorded best_value and evaluation counts.
- Extend benchmark snapshot version to include an `objectives` section.
- Update trend report Markdown for objective rows.

## Non-Goals

- New solver backends or topology integration (Stage 4).

## Functional Requirements

- `collect_domain_benchmark_snapshot` returns `version` 2 with `objectives` dict.
- Two scenarios: `sphere_dim4` and `sphere_dim8` with documented budgets.
- Performance tests enforce stable threshold bands on best_value.

## Acceptance Criteria (Checklist)

- [x] Objective helpers live in `benchmark_metrics` with isolated persistence paths.
- [x] Integration snapshot test asserts objective thresholds.
- [x] Report script renders objective table when present.
- [x] ADR documents schema/version bump rationale.

## Execution Plan

- [x] Implement `run_objective_benchmark_isolated` and snapshot aggregation.
- [x] Add performance + integration coverage.
- [x] Extend Markdown reporter and governance artifacts.

## Risks

- SciPy stochastic behavior may rarely flirt with thresholds; budgets tuned conservatively.

## Verification Link

`docs/process/verification/VR-0005-benchmark-objective-evolution.md`
