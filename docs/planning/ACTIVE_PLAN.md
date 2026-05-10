# Active Plan

## Current Phase

**Stage 3:** discrete optimizer track (see Next 3 Slices).

**Stage 2 is closed** (2026-05-11): acceptance criteria and explainability follow-up are satisfied;
domain benchmarks and integration regression gates run under CI (`integration-performance` job).

## Stage Goal (Stage 3 focus)

Continue first-class discrete support (learning → validation → refinement) while preserving the
local-first learning loop and policy model.

## Stage 2 — Complete

### Stage 2 Goal (achieved)

Move from "working local engine with guardrails" to "measured, calibrated, and release-ready."

### Stage 2 Acceptance Criteria

1. **Domain benchmark scenarios** exist and run in **CI** and local with reproducible outputs — **done**
   (`tests/performance`, `tests/integration` snapshot thresholds; CI job `integration-performance`).
2. **Learning quality trend report** is generated from benchmark runs — **done**
   (`scripts/generate_benchmark_trend_report.py`, `make report-benchmark`; PRD-0003).
3. **Strategy confidence/reward** tuned with documented rationale — **done**
   (ADR-0003, PRD-0004, calibration tests).
4. **Release flow documents** include status-check naming and multi-job CI guidance — **done**
   (`RELEASE_CHECKLIST.md`, `DEVELOPMENT_WORKFLOW.md`).

### Stage 2 Follow-up: Explainability Components — Complete

Track acceptance criteria are met: structured `explanation` on results, memory override confidence,
deterministic test paths, and integration coverage (e.g. core-depth gate, explainability tests).

Candidate slices (status):

1. Explanation schema — *(integrated; PRD-0008 / ADR-0007)*  
2. Decision trace — *(integrated via attempt traces, `selection_basis`, adaptation overlay; no separate export-only slice)*  
3. Formatter helpers — *(integrated; PRD-0015)*  
4. Explanation validation — *(integrated; integration tests + core-depth validation)*  
5. Docs — *(integrated at `SYSTEM_OVERVIEW.md`, ADRs, PRDs; user-facing tutorial backlog is non-blocking)*  

## Next 3 Slices

1. Stage 3 acceptance closure: discrete cold→warm selection evidence on validation scenarios (ties Stage 3 acceptance criterion 3).
2. Optional: wire discrete validation rows into `generate_benchmark_trend_report.py` (debt until needed).
3. Optional follow-up: Bayesian / acquisition-function hybrid outer loop beyond neighborhood refinement.

## Execution Order Gate (linear by stage number)

Stages advance in order: **2 → 3 → 4**. Later stage work is not a prerequisite for earlier stage
work.

1. **Stage 2** — Quality-to-release readiness (benchmarks in CI, calibration, reporting). **Closed.**
2. **Stage 3** — Discrete optimizers: finish validation + refinement slices and discrete cold→warm
   evidence (learning/memory slice integrated). **In progress.**
3. **Stage 4** — Full core-depth **continuous** parity with the legacy tool (topology depth,
   roster breadth, adaptive loop quality gates, etc.). **Treat remaining Stage 4 backlog as primary
   only after Stage 3 acceptance criteria are met** (or document explicit ADR exception).

**Historical note:** Some Stage 4-oriented scaffolding (topology artifact, tunneling, expanded
continuous roster, autodidactic loop, priors, core-depth tests) landed while Stage 2 was still
open. That does not redefine stage order: **Stage 3 discrete remains the current numbered focus
until its acceptance criteria are satisfied;** remaining Stage 4 acceptance checks are then closed
out against `main` deliberately in Stage 4 order.

## Stage 3 Preview: Discrete Optimizers

### Stage Goal

Add first-class support for integer and categorical decision variables while preserving
the same local-first learning loop and policy enforcement model.

### Candidate Slices

1. Problem model slice: add typed variable descriptors (`continuous`, `integer`, `categorical`).
2. Solver slice: add baseline discrete solvers (random search + local neighborhood search). *(integrated)*
3. Hybrid routing slice: route mixed-variable problems to compatible solver pipelines. *(integrated)*
4. Learning slice: capture discrete-problem features and strategy rewards in local memory. *(integrated)*
5. Validation slice: add benchmark scenarios for integer knapsack-like and scheduling-like cases. *(integrated: knapsack-01 + 2×2 assignment; `make benchmark` + integration tests)*

### Stage Acceptance Criteria

1. API supports mixed-variable specs with clear validation errors and a hybrid execution path for mixed discrete/continuous descriptors.
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

2026-05-11 — Stage 3 hybrid outer refinement (random exploration + discrete neighborhood refinement, staged inner budgets; ADR-0021 / PRD-0022 / VR-0022). Continuous bounds-only bandit excludes discrete/hybrid arms; validation benchmarks + `rng_seed` integrated; execution gate remains linear 2 → 3 → 4.
