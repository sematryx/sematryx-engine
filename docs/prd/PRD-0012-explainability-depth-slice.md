# PRD-0012: Explainability Depth Slice

## Problem Statement

Explanations did not summarize adaptation context linking topology, features, retry sequencing,
and which attempt delivered the reported optimum.

## Goals

- Emit deterministic adaptation metadata on optimization explanations.
- Cover topology hints, problem feature summaries, planned retry strategies, and winning attempt index.

## Non-Goals

- Natural-language formatting helpers (defer formatter slice).

## Functional Requirements

- Optimizer attaches nested `adaptation` mapping beside existing explanation keys.
- Values derive solely from runtime state already computed for routing/tuning.

## Acceptance Criteria (Checklist)

- [x] Explanation exposes adaptation block after optimize completes.
- [x] Winning attempt index matches minimum-loss retry ordinal.
- [x] Planned strategy ordering aligns with attempt_limit sequencing.
- [x] Governance docs updated.

## Verification Link

`docs/process/verification/VR-0012-explainability-depth-slice.md`
