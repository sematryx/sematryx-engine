# PRD-0009: Legacy Continuous Solver Roster Slice

## Problem Statement

The local engine has too few continuous strategies compared to legacy breadth, reducing routing and
learning headroom before discrete work.

## Goals

- Expand the strategy roster with additional SciPy continuous methods.
- Keep runtime local-first and dependency-stable.
- Add tests proving new methods execute and are selectable.

## Non-Goals

- No discrete solver support in this slice.
- No optional non-SciPy backends (CMA-ES/skopt) yet.

## Functional Requirements

- Add new strategy IDs in selector roster.
- Implement solver dispatch for new strategy IDs in SciPy solver module.
- Update tests to validate execution and integration selection compatibility.

## Acceptance Criteria (Checklist)

- [x] Strategy roster includes SHGO and six additional local SciPy methods.
- [x] `solve_with_scipy` dispatches each new strategy ID.
- [x] Unit + integration/smoke tests include new roster coverage.
- [x] Governance docs updated (ADR/VR/plan/changelog/debt).

## Verification Link

`docs/process/verification/VR-0009-legacy-continuous-solver-roster.md`
