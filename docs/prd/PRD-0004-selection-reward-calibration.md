# PRD: Selection and Reward Calibration

## Problem Statement

Reported strategy confidence mixed Thompson-sample draws with interpretable belief strength,
and memory override used a flat confidence. Bandit rewards used a linear inverse mapping
that can saturate too aggressively on large objective values.

## Goals

- Report bandit confidence as posterior belief for the selected strategy.
- Scale memory-override confidence with historical evidence count.
- Use smoother reward shaping for bandit updates from optimization outcomes.

## Non-Goals

- Changing solver portfolio or topology integration in this slice.
- Retraining historical bandit state files on disk automatically.

## Functional Requirements

- Stochastic bandit selection returns posterior mean of the chosen arm as confidence.
- Memory override confidence is a deterministic function of `usage_count` with a cap.
- Optimizer bandit reward uses sqrt-scaled inverse objective (documented formula).

## Acceptance Criteria (Checklist)

- [x] Unit tests cover memory confidence curve and bandit confidence semantics.
- [x] Integration test proves memory confidence increases with stored usage.
- [x] Existing benchmark and learning integration thresholds still pass.
- [x] ADR documents rationale and formulas.

## Execution Plan

- [x] Implement calibration in `bandit`, `strategy_selector`, and `optimizer`.
- [x] Add and update unit and integration tests.
- [x] Update governance artifacts and active plan progression.

## Risks

- On-disk bandit JSON from older runs remains compatible (posterior fields unchanged).

## Rollout Plan

Ship with next release; users may see slightly different confidence numbers in logs/UI.

## Verification Link

`docs/process/verification/VR-0004-selection-reward-calibration.md`
