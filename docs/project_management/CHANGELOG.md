# Changelog

## 2026-05-08

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
