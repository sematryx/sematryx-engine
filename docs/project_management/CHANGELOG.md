# Changelog

## 2026-05-11

- Stage 3 hybrid outer refinement: after random discrete shells, coordinate neighborhood refinement with staged inner SciPy budgets; public `discrete_coordinate_neighbors`; hybrid `OptimizeResult.message` `hybrid_outer_random_inner_scipy_refined`. PRD-0022 / VR-0022 / ADR-0021.
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
