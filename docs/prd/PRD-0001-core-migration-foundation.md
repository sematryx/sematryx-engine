# PRD: Core Migration Foundation

## Problem Statement

The prior project drifted from intended architecture and included shortcut implementations.
This repository needs enforced process guardrails and a minimal local-first engine foundation.

## Goals

- Enforce a plan -> execute -> verify loop
- Build a local-first optimization core with empirical learning
- Block cloud/platform coupling in core runtime

## Non-Goals

- Full parity with legacy cloud ecosystem
- Multi-node/federated orchestration in v1

## Functional Requirements

- Local optimization API and runtime path
- Local strategy memory persistence
- Structural policy checks for docs/tests/ADR

## Acceptance Criteria (Checklist)

- [x] Core optimize path executes locally and returns result object
- [x] Local strategy memory stores and returns recommendations
- [x] Policy checks enforce ADR + tests + README updates for code changes
- [x] Forbidden cloud/platform imports are blocked in core runtime

## Execution Plan

- [x] Bootstrap package and quality gates
- [x] Implement selector + solver + memory baseline
- [x] Add policy scripts and governance templates
- [x] Add tests validating learning influences selection

## Risks

- Overly strict policy checks may block legitimate workflow edge cases

## Rollout Plan

Enable branch protection after first CI pass on GitHub.

## Verification Link

`docs/process/verification/VR-0001-core-migration-foundation.md`

## Update Note (2026-05-07)

Expanded workflow enforcement with architecture overview, active plan, changelog,
integration debt tracking, and stricter policy gates.

Completed persistence of bandit state across restarts and added deterministic
integration evidence that warmed local learning influences subsequent selection.
