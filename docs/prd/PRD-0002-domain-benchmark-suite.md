# PRD: Domain Benchmark Suite

## Problem Statement

Stage 2 requires measurable evidence that local learning improves strategy selection
quality across representative domains. Existing integration tests validate specific
behaviors but do not provide scenario-based benchmark coverage with expected ranges.

## Goals

- Add reproducible domain benchmark scenarios for cold vs warm selection quality.
- Define expected metric ranges that can be validated in automated tests.
- Keep benchmark artifacts local-first and lightweight.

## Non-Goals

- Full solver-runtime benchmarking across all objective-function families.
- External dashboards or cloud-based telemetry.

## Functional Requirements

- Performance tests under `tests/performance/` for at least two domains.
- Benchmarks must report selection hit-rate and average confidence.
- Warm-history runs must show improvement over cold starts with explicit thresholds.
- Benchmark commands must be available through the project `Makefile`.

## Acceptance Criteria (Checklist)

- [x] Added `tests/performance/test_domain_benchmark_suite.py` with two domain scenarios.
- [x] Benchmarks validate cold vs warm behavior using deterministic seeds.
- [x] Warm-history selection hit rate threshold is enforced (`>= 0.95`) per scenario.
- [x] Added a `make benchmark` command for repeatable execution.

## Execution Plan

- [x] Implement benchmark helper for repeated selection measurements.
- [x] Add rugged-search domain benchmark (cold vs warm).
- [x] Add high-dimensional domain benchmark (cold vs warm).
- [x] Update Makefile and run benchmark/local quality gates.

## Risks

- Confidence thresholds could become brittle if selection policy changes significantly.

## Rollout Plan

Run benchmarks locally and in PR validation when learning-policy changes are proposed.

## Verification Link

`docs/process/verification/VR-0002-domain-benchmark-suite.md`
