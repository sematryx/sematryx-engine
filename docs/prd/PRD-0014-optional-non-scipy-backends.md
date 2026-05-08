# PRD-0014: Optional Non-SciPy Continuous Backends

## Problem Statement

Legacy parity requires non-SciPy continuous solvers, but core install should remain lightweight.

## Goals

- Wire optional CMA-ES and scikit-optimize strategy families into runtime dispatch.
- Keep default runtime stable when optional packages are absent.

## Non-Goals

- Mandatory installation of optional dependencies.
- Full hyperparameter calibration for optional backends.

## Functional Requirements

- Optional strategy detection at runtime via package availability checks.
- Selector roster extends with available optional strategies only.
- Dispatch routes non-SciPy strategy names to optional backend implementations.

## Acceptance Criteria (Checklist)

- [x] Optional strategies appear only when corresponding packages are installed.
- [x] Core runtime paths continue to pass tests without optional packages installed.
- [x] Governance docs updated (ADR/VR/plan/changelog/debt).

## Verification Link

`docs/process/verification/VR-0014-optional-non-scipy-backends.md`
