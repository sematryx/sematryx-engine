# PRD-0016: Stage 3 Typed Variable Descriptor Kickoff

## Problem Statement

API currently accepts only continuous bounds tuples and cannot validate typed variable specifications.

## Goals

- Add typed variable descriptor normalization/validation in API layer.
- Allow continuous descriptors immediately.
- Emit explicit errors for integer/categorical descriptors until solver baseline slice.

## Non-Goals

- Implementing discrete-capable solvers in this slice.

## Functional Requirements

- New descriptor module with `VariableDescriptor` contract.
- `optimize()` accepts either `bounds` or `variable_descriptors`.
- Continuous descriptors convert to bounds; integer/categorical rejected with clear message.

## Acceptance Criteria (Checklist)

- [x] Continuous descriptor path executes optimize successfully.
- [x] Integer/categorical descriptor paths fail with explicit Stage 3 kickoff errors.
- [x] Unit + integration tests added.
- [x] Governance docs updated.

## Verification Link

`docs/process/verification/VR-0016-stage3-typed-variable-descriptor-kickoff.md`
