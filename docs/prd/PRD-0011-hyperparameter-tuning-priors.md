# PRD-0011: Hyperparameter Tuning Priors Slice

## Problem Statement

Solver hyperparameters were mostly static across domains despite topology-driven retries.

## Goals

- Compute deterministic tuning priors from domain label, problem features, and topology signals.
- Scale per-attempt evaluation budgets using priors before invoking SciPy strategies.
- Surface priors and per-attempt budgets in explanations for downstream explainability.

## Non-Goals

- Bayesian optimisation over hyperparameters.
- Non-SciPy solver backends.

## Functional Requirements

- `compute_solver_tuning_priors` returns a versioned dictionary consumed by `solve_with_scipy`.
- Optimizer applies priors to each attempt and passes them through to SciPy dispatch.
- Integration tests assert explanation payloads include tuning priors and attempt budgets.

## Acceptance Criteria (Checklist)

- [x] Priors influence SciPy paths where supported (DE polish/population, DA restart ratio, SHGO sampling scale).
- [x] Attempt logs capture budget allocations post-multiplier.
- [x] Unit schema coverage plus integration presence checks exist.
- [x] Governance artifacts updated (ADR/VR/plan/changelog/debt).

## Verification Link

`docs/process/verification/VR-0011-hyperparameter-tuning-priors.md`
