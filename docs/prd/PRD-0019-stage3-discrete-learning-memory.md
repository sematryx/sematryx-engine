# PRD-0019: Stage 3 Discrete Learning + Memory Features

## Problem Statement

Typed-variable runs (`discrete_only`, `hybrid`) stored the same continuous-shaped `problem_features`
blob as bounds-only runs, so local SQLite memory could not distinguish discrete problem shape or
surface bandit reward alongside outcomes.

## Goals

- Emit compact, JSON-stable descriptor statistics on discrete and hybrid optimizer paths.
- Persist those fields in `LocalStrategyMemory.optimization_runs.features_json` together with
  `optimizer_bandit_reward` (and hybrid inner strategy label when applicable).
- Mirror a **`descriptor_learning`** snapshot under `explanation.adaptation` for debugging and reports.

## Non-Goals

- Changing recommendation ranking logic or adding SQL columns beyond existing JSON payload.
- Discrete-specific benchmark scenarios (validation slice).

## Functional Requirements

- `descriptor_learning_features()` summarizes mix class, per-kind counts, and a log-sum measure over
  discrete branch counts (integer span × categorical arity).
- Optimizer merges summary into memory payload only on discrete-only and hybrid routes.

## Acceptance Criteria (Checklist)

- [x] Discrete + hybrid runs populate memory payload extensions and adaptation snapshot.
- [x] Continuous bounds-only runs unchanged.
- [x] Unit + integration tests cover counts and hybrid mix class.
- [x] Governance artifacts updated.

## Verification Link

`docs/process/verification/VR-0019-stage3-discrete-learning-memory.md`
