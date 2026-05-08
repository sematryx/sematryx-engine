# PRD-0010: Autodidactic Loop Slice

## Problem Statement

Optimization currently executes one strategy attempt per run. Stage 4 requires bounded adaptive
retries to improve quality while respecting budgets.

## Goals

- Add bounded multi-attempt loop in optimizer.
- Choose attempt budget based on topology budget regime.
- Record attempt trace in explanation output.

## Non-Goals

- No new solver backends.
- No external orchestration or async execution.

## Functional Requirements

- Attempt limits: tight=1, moderate=2, generous=3.
- Per-attempt budget split from total evaluations.
- Keep best attempt result and persist winning strategy outcome.

## Acceptance Criteria (Checklist)

- [x] Runtime performs bounded retries for non-tight regimes.
- [x] Explanation includes attempt limit and per-attempt records.
- [x] Integration tests verify loop behavior for generous budgets.
- [x] Governance docs updated (ADR/VR/plan/changelog/debt).

## Verification Link

`docs/process/verification/VR-0010-autodidactic-loop-slice.md`
