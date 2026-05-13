# CLAUDE.md

This file is the top-of-context document for AI sessions working on sematryx-engine.
Read it first. Re-read it whenever you're about to make a substantive change.

## What this project is

**sematryx-engine** is a pip-installable local-first optimization engine. It is the
product, not a layer over a service. There is no cloud counterpart in scope.

**sematryx-api** (at `/home/workspace/sematryx-api/`) is the **deprecated** legacy
codebase. It is in the workspace for reference only — to show what algorithms have
already been thought through. The engine does **not** depend on it, does not import
from it, and is not required to maintain parity with it.

## Why governance is strict

A 2026-05-13 audit (ADR-0026, ADR-0027) found that the engine had inherited
vocabulary from sematryx-api ("Physarum tunneling", "contextual bandit", "autodidactic
loop", "topology pipeline") without porting the substance. PRDs, ADRs, VRs, and the
README accumulated claims that the code didn't deliver. The governance machinery in
this repo (PRD → ADR → VR → policy checks) exists because of that history. **Do not
weaken or work around it.** Substance > structure.

## Hard rules for AI sessions

1. **Before writing code that uses vocabulary present in the legacy api codebase,**
   check the Engine vs Legacy-API Registry in
   [`docs/process/ADOPTION_GATE.md`](docs/process/ADOPTION_GATE.md). If the term is not
   in the registry, you are about to introduce drift — stop, read the audit ADRs
   (ADR-0026, ADR-0027), and add a registry row with an explicit port/defer/drop
   decision before continuing.
2. **`scripts/check_policy.py` enforces the substance gate at CI.** If your PR adds
   identifiers from `LEGACY_API_VOCABULARY` to engine source without updating the
   registry, the build fails. This is by design.
3. **Names must describe implementation, not aspiration.** If a name implies substance
   you have not built, use the honest name (`problem_shape_classifier`, not
   `topology_pipeline`). Add `[STUB]` / `[ASPIRATIONAL]` markers in docs when the
   implementation is intentionally minimal.
4. **Claims about behaviour need behavioural backing.** If you write "X improves Y"
   in the README or an ADR, either (a) an ablation verdict supports it, (b) a
   behavioural integration test demonstrates it, or (c) the claim is marked
   `[STUB]`/`[ASPIRATIONAL]`. The verification report's Substance Audit section
   enforces this for any code under `src/`.
5. **Read these docs before substantive work:**
   - [`docs/architecture/SYSTEM_OVERVIEW.md`](docs/architecture/SYSTEM_OVERVIEW.md) —
     architecture + current substance state per subsystem
   - [`docs/planning/ACTIVE_PLAN.md`](docs/planning/ACTIVE_PLAN.md) — current
     phase, next slices, blockers
   - [`docs/process/ADOPTION_GATE.md`](docs/process/ADOPTION_GATE.md) — the registry
   - [`docs/architecture/decisions/ADR-0026-rename-shape-classifier-and-record-topology-drift.md`](docs/architecture/decisions/ADR-0026-rename-shape-classifier-and-record-topology-drift.md) — the
     topology audit (cautionary tale)
   - [`docs/architecture/decisions/ADR-0027-substance-audit-and-process-correction.md`](docs/architecture/decisions/ADR-0027-substance-audit-and-process-correction.md) — the
     audit summary and the guardrails this PR installed
6. **Verification artefacts are mandatory, not ceremonial.** Every code change under
   `src/` requires PRD, ADR (for architecture/core changes), VR, README update,
   ACTIVE_PLAN, CHANGELOG, and INTEGRATION_DEBT updates. The policy script enforces
   this. Do not try to bypass it. The VR's Substance Audit and Shortcut Audit
   sections must be honest — those are the gates that exist *because* AI sessions
   wrote unchecked claims into prior VRs and PRDs.
7. **No metaphor-driven names.** Do not call a problem-shape classifier a "topology
   pipeline" because the words sound related. Do not call a multi-attempt fallback
   loop "autodidactic" because it sounds smart. The engine pays for names with code.

## Workflow recap

The full required sequence is in
[`docs/process/DEVELOPMENT_WORKFLOW.md`](docs/process/DEVELOPMENT_WORKFLOW.md). The
short version:

1. Read ACTIVE_PLAN; pick a slice.
2. Write/update the PRD with acceptance criteria. **Declare whether criteria are
   structural or behavioural** (Acceptance Shape section).
3. Write/update the ADR if the change affects architecture.
4. Implement the slice in small vertical cuts.
5. Add/update tests in the same slice. Behavioural tests for behavioural claims.
6. Write the VR mapping each PRD criterion to evidence. Fill the Substance Audit
   and Shortcut Audit honestly.
7. Run `make all` locally (lint, typecheck, tests, policy). Fix everything before
   pushing.
8. Open PR using `.github/pull_request_template.md`.
9. Address review.
10. Merge only when `CI / required-checks` is green.

## Don't reach for new structures

The repo already has a substantial governance infrastructure under `docs/process/`,
`docs/architecture/`, `docs/prd/`. **Before proposing a new doc, audit what exists.**
The ADOPTION_GATE Decision Log + Registry, the VR template, the PRD template, and
the policy script cover most of what you'll want to add. Use them.

If you genuinely need a new artefact, add an ADR justifying it.
