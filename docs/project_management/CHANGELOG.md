# Changelog

## 2026-05-13 (PR 6 — substance audit + process guardrails)

- **ADR-0027: substance audit + process correction.** Broader audit found the engine
  inherited api vocabulary across many subsystems (bandit, learning, memory, AI,
  explainability) without porting substance. LOC ratios: bandit 37×, memory 50×,
  AI module ∞ (engine has none), explainability 16×. The topology drift caught by
  ADR-0026 was a representative sample, not an outlier.
- **Engine vs Legacy-API Registry** populated in `docs/process/ADOPTION_GATE.md`.
  Every audited subsystem gets a row with current status (stub / partial /
  fully-ported / deferred / dropped / renamed), api reference, engine reference,
  and decision rationale.
- **Substance gate in `scripts/check_policy.py`:** new `LEGACY_API_VOCABULARY`
  constant + check that scans added lines under `src/` for inherited identifiers.
  When found, requires `docs/process/ADOPTION_GATE.md` to be in the PR's changed
  files. Source-only scanning so docs can describe these terms freely.
- **VR template Substance Audit section** (`docs/process/verification/IMPLEMENTATION_VERIFICATION_TEMPLATE.md`)
  with mandatory checkboxes for substance-matches-names and doc-claims-have-backing.
  Two load-bearing phrases added to `required_tokens` in the policy script so CI
  fails if a VR omits them.
- **PRD template Acceptance Shape section** forces authors to declare each
  acceptance criterion as structural or behavioural, with at least one behavioural
  criterion required for any feature claiming user-facing value.
- **`CLAUDE.md` at repo root** as the AI top-of-context document. Short pointer doc
  stating product purpose, relationship to deprecated api, hard rules. Added to
  `REQUIRED_FILES` in the policy script.
- **`INCIDENT_RESPONSE.md`** adds documentation-drift trigger and procedure.
- **`DEVELOPMENT_WORKFLOW.md`** documents the policy-constants maintenance process
  (`REQUIRED_FILES`, `KNOWN_SUBSYSTEM_DIRS`, `LEGACY_API_VOCABULARY`) — including the
  rule that a new subsystem directory name cannot enter `KNOWN_SUBSYSTEM_DIRS` in
  the same PR that introduces the subsystem code.
- **README.md rewritten** — removed feature-accretion wall; added Current Substance
  State table referencing the registry; explicit relationship to deprecated api.
- **SYSTEM_OVERVIEW.md rewritten** — Mermaid diagram cleaned (Multi-Armed Bandit,
  not Contextual); Current Substance State table added; audit history footer added.
- **VR-0025** written documenting the ablation harness verification with the new
  Substance Audit section format.

## 2026-05-13 (PR 5)

- **ADR-0026 / PR 5 — rename topology stub to problem-shape classifier; record drift; reshape Slice 1.**
  Audit found that PRD-0006 / ADR-0005 (topology pipeline scaffold) shipped a problem-shape
  classifier (89 lines: dims + budget + bound widths → weighted sum) under topology naming,
  and that PRD-0007 / ADR-0006 ("Physarum tunneling integration") never implemented any
  Physarum machinery — it wired a hardcoded `scipy_dual_annealing` override to the shape
  classifier's output via metaphor. Mechanical rename across 30 files:
  `engine/topology.py` → `engine/problem_shape_classifier.py`; `TopologyArtifact` →
  `ProblemShape`; `physarum_tunneling_score` → `shape_routing_score`; `tunneling_directive` →
  `shape_routing_directive`; `OptimizationResult.topology_artifact` →
  `OptimizationResult.problem_shape`; `AblationConfig.topology_routing` → `shape_routing`;
  `_topology_tunneling_override` → `_shape_routing_override`; basis
  `"physarum_tunneling_override"` → `"shape_routing_override"`; scenario
  `topology_firing_current` → `shape_routing_firing_current`; explanation keys updated
  (`shape_routing_directive`, `shape_routing_score`, `budget_regime`, `complexity_hint`).
  `tuning_priors` parameter `tunneling_directive` → `shape_routing_directive`;
  `topology_budget_regime` → `budget_regime`. ADR-0005, ADR-0006, PRD-0006, PRD-0007
  marked superseded. ACTIVE_PLAN Slice 1 reshaped from "deepen Physarum tunneling
  beyond scaffolding" to **"port the real topology pipeline from the legacy api
  reference"** — Sobol decomposition + `PhysarumNetworkMapper` +
  `TopologyInformedTunneling` + `SHGOSubspaceProver`, under ablation gating, each
  piece independently measured. README and SYSTEM_OVERVIEW updated. Findings doc
  prepended with a relabel note so the v2 baseline's "topology_routing helps"
  verdict reads as "shape_routing helps" — same data, narrower claim.

## 2026-05-11

- Stage 3 optional closure: hybrid outer **LCB acquisition** over discrete shells (explore + refine), tightened inner budget splits; **descriptor_mix-scoped** SQLite recommendations (`json_extract`) with hybrid inner wiring; updated hybrid result message. PRD-0024 / VR-0024 / ADR-0023.
- Stage 3 acceptance closure: `benchmark_metrics` adds discrete knapsack/assignment cold→warm selection scenarios + seeded discrete objective rows; trend report renders all scenario/objective keys; `test_stage3_discrete_cold_warm_selection`. PRD-0023 / VR-0023 / ADR-0022.
- Stage 3 hybrid outer refinement: after random discrete shells, coordinate neighborhood refinement with staged inner SciPy budgets; public `discrete_coordinate_neighbors`; hybrid message evolved via acquisition step (see ADR-0023). PRD-0022 / VR-0022 / ADR-0021.
- Continuous-only `run_optimization` excludes discrete/hybrid strategy IDs from bandit selection so fresh CI environments cannot route bounds-only problems through `hybrid_outer_random_inner_scipy`. PRD-0021 / VR-0021 / ADR-0020; integration regression `test_continuous_bandit_excludes_hybrid_strategies`.
- Stage 3 discrete validation: knapsack-01 and 2×2 assignment toy scenarios (`discrete_benchmark_scenarios.py`), integration tests, and `make benchmark` extended; `optimize(..., rng_seed=)` threads into discrete/hybrid solver RNGs for reproducible CI.
- PRD-0020 / VR-0020 / ADR-0019.
- Stage 3 learning slice: discrete/hybrid runs persist `descriptor_learning_features` plus `optimizer_bandit_reward` (and hybrid inner strategy) in local memory JSON; explanations expose `adaptation.descriptor_learning`.
- PRD-0019 / VR-0019 / ADR-0018; `ACTIVE_PLAN` candidate slice 4 marked integrated and Next 3 Slices rolled forward.
- `ACTIVE_PLAN.md`: execution gate rewritten as linear Stage 2 → 3 → 4 (removed contradictory “Stage 3 after Stage 4” rule); noted early Stage 4 scaffolding vs current Stage 3 focus.
- CI: added `integration-performance` job running `pytest tests/integration tests/performance --import-mode=importlib`; `required-checks` now depends on it.
- Stage 2 closed in `ACTIVE_PLAN.md`: acceptance criteria and explainability follow-up marked complete; current execution focus set to Stage 3 discrete track.
- `RELEASE_CHECKLIST.md` / `check_release_checklist.py` / `DEVELOPMENT_WORKFLOW.md` updated for the expanded CI matrix.

## 2026-05-10

- Stage 3 hybrid routing: mixed `variable_descriptors` (continuous + integer/categorical) run `hybrid_outer_random_inner_scipy` (random discrete outer samples + inner continuous optimization); selector gains `exclude_strategies` so inner solves cannot pick discrete-only arms.
- Added `descriptors_to_mixed_encoded_bounds`, `normalize_mixed_solution`, and `solvers/hybrid_solvers.py`.

## 2026-05-09

- Stage 3 discrete solver baseline: discrete-only `variable_descriptors` (`integer` / `categorical`) optimize via `discrete_random_neighborhood` (random search + coordinate neighborhood refinement); mixed continuous + discrete still raises until hybrid routing slice.
- Descriptor helpers: `classify_descriptor_mix`, `descriptors_to_encoded_bounds`; bandit roster extended with the discrete strategy arm.

## 2026-05-08

- Added Stage 3 typed variable descriptor kickoff: continuous descriptors run now, integer/categorical descriptors validate then raise explicit "not yet supported" errors until solver baseline slice.
- Added explanation formatter helpers (concise + verbose) for structured explanation payloads and exported them in the package API.
- Added optional non-SciPy continuous backend wiring (CMA-ES + scikit-optimize families) behind runtime availability detection and strategy dispatch.
- Added core-depth parity regression gate test covering snapshot thresholds and full runtime contract surface (topology, adaptation, priors, attempts).
- Extended explanations with adaptation depth (topology/problem summaries, planned retries, winning attempt index).
- Added deterministic hyperparameter tuning priors from domain/topology/features; scaled autodidactic attempt budgets and SciPy knobs (DE polish/population, DA restart ratio, SHGO sampling) with explanation surfacing.
- Added bounded autodidactic retry loop (topology-budgeted attempts) and explanation attempt traces; optimizer now selects best attempt result.
- Expanded continuous solver roster with additional SciPy methods (`shgo`, `powell`, `tnc`, `slsqp`, `cobyla`, `nelder-mead`, `cg`) and wired selector compatibility.
- Added explanation schema contract on optimization results, including deterministic selection basis/confidence and topology tunneling evidence.
- Integrated Physarum-network signal into topology-driven tunneling selection: topology now emits `physarum_tunneling_score`/`tunneling_directive`, and selector routes aggressive cases to tunneling strategy.
- Added Stage 4 topology kickoff scaffold: deterministic topology artifact is now emitted on optimization results with baseline unit/integration tests.
- Documented mandatory Physarum-network-to-tunneling integration requirement for upcoming topology-solver integration slice.
- Documented execution order: legacy continuous solver roster in Stage 4 before Stage 3 discrete; added Stage 4 slice and acceptance criterion for portfolio parity.
- Split CI into parallel jobs (`lint`, `typecheck`, `unit-smoke`, `policy`) with aggregate `required-checks` gate; updated release and workflow docs for branch protection naming.
- Extended domain benchmark snapshot to version 2 with isolated sphere objective runs (`objectives` section).
- Added performance coverage for objective benchmark thresholds and integration asserts aligned with the snapshot contract.
- Benchmark trend Markdown report includes an objective-quality table when objectives are present.

## 2026-05-07

- Bootstrapped `sematryx-engine` local-first package scaffold.
- Added governance enforcement: PRD, ADR, verification, and policy scripts.
- Added local strategy memory with SQLite and learning-influenced strategy selection.
- Added integration and unit tests for learning-path behavior.
- Added persisted bandit posterior state to local JSON for restart continuity.
- Added deterministic warm-state integration coverage for selector behavior.
- Added repeated-run integration coverage for cold vs warm domain selection quality.
- Replaced CI template with executable workflow and added release-checklist policy check.
- Defined Stage 2 plan for quality-to-release readiness with concrete PR slices.
- Added Stage 2 benchmark suite with reproducible domain scenarios and `make benchmark`.
- Enabled strict policy mode requiring new PRD/VR files per source slice and new ADRs for core behavior changes.
- Added Stage 2 explainability follow-up track with slice-level roadmap and acceptance criteria.
- Added Stage 4 preview for full core-depth parity including topology-to-solver integration.
- Added enforceable Adoption Gate workflow and policy checks for new subsystem integrations.
- Reordered execution sequence to complete benchmark-depth slices before Stage 4, with Stage 3 deferred until after Stage 4 parity.
- Added `benchmark_metrics` module and benchmark trend report CLI with JSON/Markdown output (`make report-benchmark`).
- Calibrated selection confidence (posterior mean + evidence-scaled memory override) and sqrt-scaled bandit rewards from optimization outcomes.
