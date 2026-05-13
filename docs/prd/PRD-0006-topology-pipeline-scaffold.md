# PRD-0006: Stage 4 Topology Pipeline Kickoff

> **Status: Superseded by ADR-0026** (2026-05-13). The artifact this PRD scoped as a
> "topology pipeline scaffold" is now correctly named `problem_shape_classifier` — it
> classifies problems by problem-space shape (dimensions, bounds, budget), not by
> landscape topology. The acceptance criteria below are still met at the classifier
> level; the framing of "scaffold for a real topology pipeline" is replaced by Stage 4
> Slice 1, which ports the real pipeline from the legacy api reference.

## Problem Statement

Stage 4 depends on topology-driven routing and adaptation, but runtime outputs currently expose no
topology artifact.

## Goals

- Create a deterministic topology artifact from bounds and evaluation budget.
- Attach topology artifact to optimization results without changing routing behavior.
- Add baseline tests that validate schema and end-to-end presence in `optimize()`.

## Non-Goals

- No solver routing changes in this slice.
- No new external dependencies or remote services.

## Functional Requirements

- New topology builder in `src/sematryx_engine/engine/topology.py`.
- `OptimizationResult` supports optional `topology_artifact`.
- `run_optimization` always returns a topology artifact.

## Acceptance Criteria (Checklist)

- [x] Artifact includes version, dimensions, span profile, budget regime, complexity hint.
- [x] Integration test verifies `optimize()` returns topology artifact.
- [x] Existing optimize behavior remains functional.
- [x] Governance docs (ADR/VR/plan/changelog/debt) updated.

## Verification Link

`docs/process/verification/VR-0006-topology-pipeline-scaffold.md`
