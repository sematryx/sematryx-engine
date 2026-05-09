# PRD-0017: Stage 3 Discrete Solver Baseline

## Problem Statement

Integer and categorical descriptors were validated but could not be optimized; users need a first discrete-capable execution path before hybrid mixed-variable routing.

## Goals

- Execute **discrete-only** problems (`integer` and/or `categorical`, no `continuous` in the same call) through a documented baseline strategy.
- Preserve the continuous descriptor path and explicit rejection for **mixed** continuous + discrete until the hybrid routing slice.

## Non-Goals

- Mixed-variable problems in one `optimize()` call.
- Portfolio parity with legacy discrete optimizers beyond this baseline.

## Functional Requirements

- Random search plus coordinate neighborhood refinement over encoded discrete vectors (`float` indices per existing objective signature).
- Strategy name `discrete_random_neighborhood` registered for bandit/memory updates.
- Topology/features use encoded bounds derived from descriptors.

## Acceptance Criteria (Checklist)

- [x] Discrete-only descriptor runs return finite solutions and populate explanations with discrete selection basis.
- [x] Mixed continuous + discrete raises a clear `ValueError` referencing hybrid routing.
- [x] Unit + integration tests cover integer, categorical, and mixed rejection.
- [x] Governance docs updated.

## Verification Link

`docs/process/verification/VR-0017-stage3-discrete-solver-baseline.md`
