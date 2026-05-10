# PRD-0024: Stage 3 Optional Follow-Ups Closure

## Problem Statement

`ACTIVE_PLAN` listed optional Stage 3 items: acquisition-style hybrid outer search,
descriptor-scoped memory recommendations, and outer/inner budget tightening.

## Goals

- Implement **LCB acquisition** scheduling for hybrid discrete outer loops (explore + refine).
- Add **`descriptor_mix` SQLite filter** for strategy recommendations with hybrid inner wiring.
- Refresh governance (`ACTIVE_PLAN` stale gate paragraph, Stage 4 primary focus).
- Clear matching **INTEGRATION_DEBT** deferrals that are now addressed.

## Non-Goals

- Full Bayesian GP outer loop or new optional ML dependencies.
- Changing composite hybrid bandit arm naming.

## Acceptance Criteria (Checklist)

- [x] Hybrid solver uses acquisition scoring + updated message string.
- [x] `LocalStrategyMemory.get_strategy_recommendations(descriptor_mix=...)` with JSON filter + fallback.
- [x] Hybrid optimizer passes `memory_descriptor_mix=\"mixed\"` into inner selection.
- [x] Integration test proving mixed filter differs from domain-only rankings.
- [x] ADR-0023 / VR-0024; `ACTIVE_PLAN` historical paragraph corrected.

## Verification Link

`docs/process/verification/VR-0024-stage3-optional-follow-ups-closure.md`
