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

1. Calibration slice: tune selection confidence/reward behavior and lock with tests.
2. Benchmark evolution slice: add objective-level quality metrics beyond strategy hit-rate.
3. Release-hardening docs slice: status-check naming and multi-job CI branch-rule guidance.

## Planned Follow-up Slices

4. Stage 4 kickoff slice: topology pipeline scaffolding and baseline integration tests.

## Stage 2 Follow-up: Explainability Components

### Track Goal

Produce stable, auditable explanations for strategy and solver decisions so users can
understand "why this path was chosen" and compare behavior across cold vs warm runs.

### Candidate Slices

1. Explanation schema slice: define structured explanation payload in result model.
2. Decision trace slice: capture selector and memory decision breadcrumbs in runtime.
3. Formatter slice: add concise and verbose explanation rendering helpers.
4. Explanation validation slice: add deterministic tests for explanation completeness.
5. Docs slice: document explanation contract and examples for users.

### Track Acceptance Criteria

1. Result object includes structured explanation fields for selection rationale.
2. Warm-history decisions expose memory evidence and confidence basis.
3. Explanation output is deterministic for deterministic benchmark/test paths.
4. Explanation behavior is covered by integration tests and verification artifacts.

## Execution Order Gate

Stage 4 begins only after Stage 2 benchmark-depth slices are complete (reporting,
calibration, and objective-level benchmark evolution). Stage 3 discrete optimizers begin
after Stage 4 core-depth parity slices have established stable topology-driven routing and
adaptive loops.

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

## Stage 4 Preview: Full Core-Depth Parity

### Stage Goal

Reach legacy core-engine depth (minus cloud dependencies) with integrated topology,
adaptive solving loops, richer learning, and complete explainability in the local engine.

### Candidate Slices

1. Topology pipeline slice: implement topology characterization outputs as a first-class
   planning artifact for each optimization run.
2. Topology-solver integration slice: wire topology signals directly into solver routing,
   initialization, and parameter defaults.
3. Autodidactic loop slice: add multi-attempt adaptive retry workflow with bounded budgets.
4. Hyperparameter tuning slice: add local tuning priors per domain/problem features.
5. Explainability depth slice: include topology evidence and adaptation decisions in traces.
6. Core-depth validation slice: add parity-oriented integration benchmarks and regression gates.

### Stage Acceptance Criteria

1. Every optimization run records topology analysis and uses it in solver workflow decisions.
2. Solver routing and initial parameterization are measurably influenced by topology signals.
3. Multi-attempt adaptive loop improves quality on defined benchmark classes.
4. Hyperparameter priors improve warm-run performance against default baselines.
5. Explanation output includes topology rationale, adaptation steps, and final decision basis.

## Blockers

- None.

## Last Updated

2026-05-07
