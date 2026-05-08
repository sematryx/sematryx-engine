# PRD-0008: Explanation Schema Slice

## Problem Statement

Users need stable rationale details for strategy decisions. Current output lacks a structured
explanation contract suitable for deterministic validation.

## Goals

- Introduce structured explanation payload on optimization result.
- Capture selection basis (bandit/memory/physarum) and confidence.
- Include topology tunneling evidence fields in the explanation.

## Non-Goals

- No human-readable formatter implementation in this slice.
- No UI or external logging integration.

## Functional Requirements

- `OptimizationResult` supports optional `explanation` dict.
- `run_optimization` populates explanation fields deterministically.
- Tests validate schema presence and basis values.

## Acceptance Criteria (Checklist)

- [x] Result includes `explanation` when optimize is called.
- [x] Explanation includes basis, confidence, strategy, and topology tunneling evidence.
- [x] Unit/integration tests cover schema and allowed basis values.
- [x] Governance docs updated (ADR/VR/plan/changelog).

## Verification Link

`docs/process/verification/VR-0008-explanation-schema-slice.md`
