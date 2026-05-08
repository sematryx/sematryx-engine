# PRD-0015: Explanation Formatter Slice

## Problem Statement

Users need human-friendly explanation summaries, but current API returns only structured dictionaries.

## Goals

- Add concise formatter for one-line summaries.
- Add verbose formatter including adaptation/attempt details.
- Export helper functions in package public API.

## Non-Goals

- Markdown/HTML renderer integrations.

## Functional Requirements

- `format_explanation_concise(result)` returns a compact single-line string.
- `format_explanation_verbose(result)` returns multi-line deterministic detail output.
- Unit tests validate key sections are emitted.

## Acceptance Criteria (Checklist)

- [x] Both formatter functions implemented and exported.
- [x] Unit tests cover concise + verbose output.
- [x] Governance docs updated (ADR/VR/plan/changelog/debt).

## Verification Link

`docs/process/verification/VR-0015-explanation-formatter-helpers.md`
