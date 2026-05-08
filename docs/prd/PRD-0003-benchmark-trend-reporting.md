# PRD: Benchmark Trend Reporting

## Problem Statement

Domain benchmarks exist under `tests/performance/`, but there is no single reusable
metric collector or CLI to emit JSON/Markdown snapshots for trend tracking.

## Goals

- Centralize benchmark metric computation in the engine package for reuse by tests and tooling.
- Provide a script that emits structured JSON and optional Markdown summaries.
- Keep outputs local-first with no cloud dependencies.

## Non-Goals

- Historical time-series database or hosted dashboards.
- Changing solver selection policy in this slice.

## Functional Requirements

- Shared metric functions used by performance tests and report generator.
- CLI writes JSON (stdout or file) and optional Markdown file.
- Makefile target documents the reporting workflow.

## Acceptance Criteria (Checklist)

- [x] `benchmark_metrics` module exposes snapshot collection aligned with performance tests.
- [x] `scripts/generate_benchmark_trend_report.py` produces JSON + Markdown.
- [x] Integration test validates snapshot thresholds match benchmark suite intent.
- [x] Documentation references report generation in README.

## Execution Plan

- [x] Extract metrics into `src/sematryx_engine/engine/benchmark_metrics.py`.
- [x] Refactor performance tests to call shared helpers.
- [x] Add report script and Makefile target.
- [x] Add integration coverage and governance artifacts.

## Risks

- Snapshot runtime scales with `--runs`; default kept at 100 for parity with tests.

## Rollout Plan

Developers run `make report-benchmark` or file outputs before calibration slices.

## Verification Link

`docs/process/verification/VR-0003-benchmark-trend-reporting.md`
