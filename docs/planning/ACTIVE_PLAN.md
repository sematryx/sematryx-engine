# Active Plan

## Current Phase

**Stage 4:** core-depth continuous parity — topology integration depth, roster breadth, adaptive
loop quality gates (see Stage 4 Preview).

**Stage 3 is closed** (2026-05-11): numbered acceptance criteria satisfied; optional acquisition +
descriptor-scoped memory slices integrated (ADR-0023).

**Stage 2 is closed** (2026-05-11): acceptance criteria and explainability follow-up are satisfied;
domain benchmarks and integration regression gates run under CI (`integration-performance` job).

## Stage Goal (Stage 3 focus)

**Achieved (2026-05-11):** discrete descriptors, hybrid routing, learning/memory fields, validation
benchmarks, cold→warm evidence, trend snapshots, hybrid outer refinement + LCB acquisition, and
descriptor_mix-scoped inner recommendations — without weakening the local-first policy model.

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

1. **Stage 4 topology–solver integration — expand firing-scenario coverage, then deepen.**
   v2 baseline (`docs/process/verification/baselines/FINDINGS-pre-stage-4-ablation.md`) shows
   `topology_routing` *helps* (Δ=+71%, p<0.001) on the single firing scenario we built
   (`topology_firing_current`: 13D rugged, tight budget). The inverted-heuristic hypothesis from
   the v1 reshape is **withdrawn**. Slice 1 ordered tasks:
   (a) build additional firing scenarios at other (complexity, budget_regime, landscape)
   combinations — e.g. 13D smooth, 8D tight rugged, 20D generous; measure each with
   `make ablation`; (b) if the override helps on most, deepen Physarum signal extraction
   (richer score components, more directives) — otherwise re-evaluate the heuristic with the
   broader data; (c) `make ablation` regression gate at each step.
2. Stage 4 legacy continuous roster: close parity gaps called out in subsystem docs / debt register.
   Note: `hybrid_outer_refinement` is *load-bearing* on `hybrid_separating` (without it the hybrid
   solver misses the optimum by ~4). Roster changes that touch the hybrid path must preserve this.
3. Stage 4 autodidactic loop: measurable improvements on expanded benchmark classes (ties Stage 4
   acceptance criterion 5). v2 baseline confirms `autodidactic_loop` helps on rugged multimodal
   (Δ=+48% when off under warmup; was +100% cold in v1). Expansion targets are new problem classes
   where the multi-attempt loop should compound (deceptive landscapes, multi-basin objectives).

## Deferred optional engine work

Not Stage 4 gates; tracked so it is not dropped.

- **Hybrid outer — full Bayesian / GP / Thompson discrete-shell search:** deferred (current outer uses
  LCB-style shell statistics). See **ADR-0023 § Alternatives** and **`INTEGRATION_DEBT.md`** (hybrid
  outer surrogate row).

## Execution Order Gate (linear by stage number)

Stages advance in order: **2 → 3 → 4**. Later stage work is not a prerequisite for earlier stage
work.

1. **Stage 2** — Quality-to-release readiness (benchmarks in CI, calibration, reporting). **Closed.**
2. **Stage 3** — Discrete optimizers: validation, refinement, learning, cold→warm evidence, trend
   snapshots, and optional acquisition + descriptor_mix memory **complete** (2026-05-11).
   **Closed.**
3. **Stage 4** — Full core-depth **continuous** parity with the legacy tool (topology depth,
   roster breadth, adaptive loop quality gates, etc.). **Primary numbered focus now** that Stage 3
   is closed (or document explicit ADR exception if reprioritizing).

**Historical note:** Stage 4-oriented scaffolding (topology artifact, tunneling, expanded
continuous roster, autodidactic loop, priors, core-depth tests) landed incrementally while Stage 2
and Stage 3 were open. **Stage order stays 2 → 3 → 4:** Stage 3 discrete work and its optional
follow-ups are finished (2026-05-11); remaining roadmap execution continues under **Stage 4**
unless an ADR records an explicit gate exception.

## Stage 3 Preview: Discrete Optimizers

### Stage Goal

Add first-class support for integer and categorical decision variables while preserving
the same local-first learning loop and policy enforcement model. **Met.**

### Candidate Slices

1. Problem model slice: add typed variable descriptors (`continuous`, `integer`, `categorical`).
2. Solver slice: add baseline discrete solvers (random search + local neighborhood search). *(integrated)*
3. Hybrid routing slice: route mixed-variable problems to compatible solver pipelines. *(integrated)*
4. Learning slice: capture discrete-problem features and strategy rewards in local memory. *(integrated)*
5. Validation slice: add benchmark scenarios for integer knapsack-like and scheduling-like cases. *(integrated: knapsack-01 + 2×2 assignment; `make benchmark` + integration tests)*
6. Optional closure slice: hybrid outer LCB acquisition + descriptor_mix-scoped memory for inner SciPy selection. *(integrated; ADR-0023)*

### Stage Acceptance Criteria

1. API supports mixed-variable specs with clear validation errors and a hybrid execution path for mixed discrete/continuous descriptors.
2. At least two discrete-capable strategies are available in the runtime path.
3. Strategy selection quality improves from cold to warm history on discrete benchmarks — **met**
   (`benchmark_metrics` discrete cold/warm scenarios + `test_stage3_discrete_cold_warm_selection`).
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

2026-05-11 — Stage 3 optional closure (ADR-0023): hybrid LCB acquisition outer loop + descriptor_mix SQLite memory filter + hybrid inner wiring; ACTIVE_PLAN Stage 4 primary; stale gate paragraph corrected. Prior: acceptance closure + hybrid refinement + validation + bandit guard.

2026-05-12 — Full Bayesian / GP / Thompson hybrid **outer** loop explicitly listed under Deferred optional engine work and expanded in `INTEGRATION_DEBT.md`.

2026-05-12 — Pre-Stage-4 ablation baseline (PRD-0025 / ADR-0024) committed under
`docs/process/verification/baselines/`. Findings: `autodidactic_loop` and `tuning_priors` are
statistically significant helpers; `topology_routing` shows zero measurable effect on every
scenario. Slice 1 scope reshaped — scenario design before deepening.

2026-05-13 — Follow-up analysis of the topology_routing "no effect" verdict: the override's
firing gate never opens under any tested scenario (`physarum_tunneling_score` tops out at 0.693,
threshold is 0.75), and the underlying `budget_factor` mapping in `topology.py` appears to
have its sign inverted (currently routes aggressive global search at *tight* budgets, where
`scipy_dual_annealing` cannot converge). Slice 1 reshape now records the heuristic fix as an
ordered prerequisite to any deepening work. See findings doc for hypothesis tests and
predictions.

2026-05-13 — Ablation harness v2 ships with warmup phase (ADR-0025), firing scenario
(`topology_firing_current`), and separating hybrid scenario (`hybrid_separating`). New heavy
baseline (`ablation_pre-stage-4-v2`) gives every knob a verdict. **Inverted-heuristic hypothesis
is withdrawn:** `topology_routing` measurably *helps* (Δ=+71%, p<0.001) on the firing scenario —
forced `scipy_dual_annealing` beats the bandit's natural mix on 13D tight-budget rugged. Slice 1
reshape updated to "expand firing-scenario coverage, then deepen" rather than "fix the heuristic
first." Confirmed helpers: `topology_routing`, `autodidactic_loop`, `tuning_priors`,
`hybrid_outer_refinement`. Still "no effect" under tested scenarios: `continuous_bandit`,
`descriptor_mix_memory`, `hybrid_outer_acquisition`. `memory_override` shifts the rank
distribution without moving the median.
