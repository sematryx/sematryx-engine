# PRD-0013: Core-Depth Validation Slice

## Problem Statement

Recent Stage 4 increments lack a single parity-oriented regression gate validating benchmark quality
and runtime explainability/adaptation contract together.

## Goals

- Add integration regression validating snapshot thresholds and runtime contract surfaces.
- Gate topology, attempt-loop, tuning-prior, and adaptation outputs in one test path.

## Non-Goals

- External benchmark infrastructure.
- New solver capabilities.

## Functional Requirements

- Integration test covers snapshot `version` and objective quality thresholds.
- Integration test verifies optimize result includes topology, strategy roster validity,
  attempts/budgets, tuning priors, and adaptation winning-attempt linkage.

## Acceptance Criteria (Checklist)

- [x] New core-depth validation integration test exists and passes in local/CI runs.
- [x] Test checks objective benchmark thresholds and runtime parity contract fields.
- [x] Governance docs updated (ADR/VR/plan/changelog/debt).

## Verification Link

`docs/process/verification/VR-0013-core-depth-validation-gates.md`
