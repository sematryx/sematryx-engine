# Active Plan

## Current Phase

Stage 2: quality-to-release readiness.

## Stage Goal

Move from "working local engine with guardrails" to "measured, calibrated, and release-ready."

## Stage Acceptance Criteria

1. Domain benchmark scenarios exist and run in CI/local with reproducible outputs.
2. Learning quality trend report is generated from benchmark runs.
3. Strategy confidence/reward behavior is tuned with documented rationale.
4. Release flow documents include status-check naming and multi-job CI guidance.

## Next 3 Slices

1. Reporting slice: add lightweight trend report generation from benchmark outputs.
2. Calibration slice: tune selection confidence/reward behavior and lock with tests.
3. Release-hardening docs slice: status-check naming and multi-job CI branch-rule guidance.

## Planned Follow-up Slice

4. Benchmark evolution slice: add objective-level quality metrics beyond strategy hit-rate.

## Stage 3 Preview: Discrete Optimizers

### Stage Goal

Add first-class support for integer and categorical decision variables while preserving
the same local-first learning loop and policy enforcement model.

### Candidate Slices

1. Problem model slice: add typed variable descriptors (`continuous`, `integer`, `categorical`).
2. Solver slice: add baseline discrete solvers (random search + local neighborhood search).
3. Hybrid routing slice: route mixed-variable problems to compatible solver pipelines.
4. Learning slice: capture discrete-problem features and strategy rewards in local memory.
5. Validation slice: add benchmark scenarios for integer knapsack-like and scheduling-like cases.

### Stage Acceptance Criteria

1. API supports mixed-variable bounds/specs with clear validation errors.
2. At least two discrete-capable strategies are available in the runtime path.
3. Strategy selection quality improves from cold to warm history on discrete benchmarks.
4. Docs and verification artifacts are added for each slice (PRD + verification report).

## Blockers

- None.

## Last Updated

2026-05-07
