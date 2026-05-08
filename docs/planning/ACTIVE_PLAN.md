# Active Plan

## Current Phase

Stage 2: quality-to-release readiness.

## Stage Goal

Move from "working local engine with guardrails" to "measured, calibrated, and release-ready."

## Stage Acceptance Criteria

1. Domain benchmark scenarios exist and run in CI/local with reproducible outputs.
2. Learning quality trend report is generated from benchmark runs.
3. Strategy confidence/reward behavior is tuned with documented rationale.
4. Release flow documents include status-check naming and multi-job CI guidance (done).

## Next 3 Slices

1. Stage 3 kickoff slice: typed variable descriptors for continuous/integer/categorical problems.
2. Stage 3 solver baseline slice: random-search and neighborhood discrete strategies.
3. Stage 3 hybrid routing slice: mixed-variable routing and validation gates.

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

Stage 4 begins only after Stage 2 benchmark-depth slices are complete: reporting (done),
calibration (done), and objective-level benchmark evolution (done).

**Legacy continuous solver roster (non-discrete parity with the legacy tool)** is integrated during
Stage 4—alongside topology-driven routing and adaptive workflow—not after Stage 3 discrete work.
Rationale: the legacy roster matches today’s continuous problem model; discrete optimizers require
typed variables, hybrid routing, and additional solvers. Bolting many continuous strategies on before
routing discipline exists dilutes learning signal; expanding the roster once topology and selection
can use richer signals matches the Stage 4 goal.

Stage 3 discrete optimizers begin only after Stage 4 core-depth parity slices have established
stable topology-driven routing, adaptive loops, and **legacy-continuous solver portfolio parity**
(or an explicitly documented subset with INTEGRATION_DEBT for the remainder).

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
   - Required enhancement: integrate Physarum-network signals into solver tunneling decisions;
     this was missing in the original topology solver and is mandatory for parity.
3. Legacy continuous solver roster slice: port the legacy tool’s non-discrete strategy set
   (SciPy family, scikit-optimize, CMA-ES, and other optional local-first backends) behind a
   registry with optional dependencies, bandit arms, memory keys, and benchmarks per solver class.
4. Autodidactic loop slice: add multi-attempt adaptive retry workflow with bounded budgets.
5. Hyperparameter tuning slice: add local tuning priors per domain/problem features.
6. Explainability depth slice: include topology evidence and adaptation decisions in traces.
7. Core-depth validation slice: add parity-oriented integration benchmarks and regression gates.

### Stage Acceptance Criteria

1. Every optimization run records topology analysis and uses it in solver workflow decisions.
2. Solver routing and initial parameterization are measurably influenced by topology signals.
3. Physarum-network output is consumed by the tunneling step and verified in integration tests.
4. The continuous strategy set matches legacy breadth (or documented parity subset + debt for deferrals).
5. Multi-attempt adaptive loop improves quality on defined benchmark classes.
6. Hyperparameter priors improve warm-run performance against default baselines.
7. Explanation output includes topology rationale, adaptation steps, and final decision basis.

## Blockers

- None.

## Last Updated

2026-05-08
