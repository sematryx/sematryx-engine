# ADR-0027: Substance Audit and Process Correction

## Status

Accepted

## Context

ADR-0026 documented one specific drift: the engine's `topology.py` was an 89-line
problem-shape classifier wearing topology vocabulary inherited from the legacy
sematryx-api codebase, while the api had a substantive ~2,278-line topology pipeline
that was never ported. The rename (PR 5) closed that one instance.

A broader audit (this ADR) found the topology incident was a representative sample,
not an outlier. Comparing engine subsystems to their api equivalents:

| Subsystem | API LOC | Engine LOC | Gap |
|---|---:|---:|---:|
| Topology pipeline | ~2,278 | 89 | ~26× |
| Contextual bandit | ~2,460 | 67 | ~37× |
| Memory / knowledge | ~8,394 | 166 | ~50× |
| AI / intelligence | ~31,251 | 0 | ∞ |
| Explainability | ~1,151 + design doc | 71 | ~16× |
| Learning (meta + transfer + persistence) | ~1,961 | partial (persistence only) | major |

The engine had inherited the api's **vocabulary** (Physarum, tunneling, contextual,
autodidactic, meta-learning, knowledge-graph, etc.) without inheriting the
**implementations**. Documentation accumulated marketing claims based on the names,
not the code. AI sessions (Cursor, Claude) writing each slice saw the inherited
names in surrounding docs and produced more docs that compounded the drift.

The existing governance machinery (PRD → ADR → VR, `scripts/check_policy.py`,
pre-commit hooks, CI's `required-checks` gate) was rigorous about **structural**
checks — required files exist, required sections present, required artefacts
added — but silent on **substance** — does the implementation deliver what the names
imply? PRD-0006 ("topology pipeline scaffold") satisfied all acceptance criteria at
the scaffold level. VR-0006's Shortcut Audit accepted "scaffold, real integration
not required this slice." The CI passed. The drift accumulated for ~6 weeks before
the ablation harness surfaced it.

## Decision

Install machine-checkable substance gates that close the loophole, using the
existing governance infrastructure wherever possible.

### 1. Engine vs Legacy-API Registry

Add a registry section to [`docs/process/ADOPTION_GATE.md`](../../process/ADOPTION_GATE.md)
that records every named subsystem from sematryx-api alongside its current engine
status (`stub` / `partial-port` / `fully-ported` / `deferred` / `dropped` / `renamed`)
with an explicit decision rationale and last-verified date.

The registry is the canonical answer to "does the engine implement what its names
imply?" Pre-populated with rows for the audited subsystems (topology pipeline,
contextual bandit, meta-learning, transfer learning, learning persistence, vector
memory, knowledge graph, temporal intelligence, AI module, explainability,
autodidactic loop, domain libraries).

### 2. Substance gate in `scripts/check_policy.py`

Add `LEGACY_API_VOCABULARY` constant: a `frozenset[str]` of identifiers inherited
from sematryx-api. Add a check that scans added lines under `src/` in the PR diff
(via `git diff --unified=0`) for any of these terms. When any are found, require
`docs/process/ADOPTION_GATE.md` to be in the PR's changed files. This runs in CI's
`policy` job and fails the build otherwise.

The check fires on **additions only** so historical stubs (until renamed under
ADR-0026's pattern) do not trip the gate. It scans **source code only** — docs are
explicitly where these terms get documented, so the registry section can describe
them without tripping the check on itself.

### 3. Substance Audit section in the VR template

[`IMPLEMENTATION_VERIFICATION_TEMPLATE.md`](../../process/verification/IMPLEMENTATION_VERIFICATION_TEMPLATE.md)
gains a `## Substance Audit (ADR-0027)` section with three checkboxes:

- Implementation matches what names imply (no inherited vocabulary without a registry decision).
- Doc claims about behaviour have a behavioural test or ablation verdict, or are marked `[STUB]`/`[ASPIRATIONAL]`.
- If PRD acceptance criteria are structural only, the PRD's Acceptance Shape section calls that out.

`scripts/check_policy.py`'s `required_tokens` list is extended to require the two
load-bearing phrases ("Implementation matches what names imply" and "Doc claims
about behavior have a behavioral test or ablation verdict") in every VR. CI fails
if a VR omits them — authors cannot silently elide the substance audit.

### 4. PRD Acceptance Shape

[`PRD-template.md`](../../prd/PRD-template.md) gains an `## Acceptance Shape` section
where authors must declare for each acceptance criterion whether it is **structural**
(file exists, field present, function callable) or **behavioural** (verified by a
behavioural test or ablation verdict). At least one behavioural criterion is required
for any feature claiming user-facing value.

This closes the PRD-0006 loophole, where all four acceptance criteria were structural
and the implementation satisfied them at scaffold level while the names implied
substance.

### 5. AI top-of-context document

Add [`CLAUDE.md`](../../../CLAUDE.md) at the repository root. Short pointer doc that
AI sessions read first. States the product purpose (pip-installable local optimization
engine, no cloud counterpart), the relationship to the deprecated api codebase
(reference only, do not depend), the hard rules for substantive work, and links to
the relevant docs. Mirrors the role `.cursor/rules/` plays for Cursor sessions.

Added to `REQUIRED_FILES` in `check_policy.py` so its absence is a CI failure.

### 6. Incident-response trigger for documentation drift

[`INCIDENT_RESPONSE.md`](../../process/INCIDENT_RESPONSE.md) gains a documentation-drift
trigger and procedure. When future audits surface another instance of this pattern,
there's a documented path: scope the audit, write the findings ADR, update the
registry, propose corrections in a follow-up PR.

### 7. Policy-constants maintenance process

[`DEVELOPMENT_WORKFLOW.md`](../../process/DEVELOPMENT_WORKFLOW.md) gains a section
documenting how `REQUIRED_FILES`, `KNOWN_SUBSYSTEM_DIRS`, and `LEGACY_API_VOCABULARY`
get updated. Specifically: do not add a new directory name to
`KNOWN_SUBSYSTEM_DIRS` in the same PR that introduces the subsystem code — the
adoption-gate trigger must fire on the introduction PR. Weakening any gate requires
an ADR; routine maintenance requires a CHANGELOG entry.

### 8. Audit-and-correct existing docs

Audit and rewrite [`README.md`](../../../README.md) and
[`SYSTEM_OVERVIEW.md`](../../architecture/SYSTEM_OVERVIEW.md) to remove overclaims
identified in this audit (autodidactic, contextual, adaptation overlay tying,
parity-oriented, domain-label-derived, etc.). Replace the README's "Governance"
feature-accretion wall with a product description that points at SYSTEM_OVERVIEW and
the registry. Future drift in README has to clear the substance gate in PRs that
modify it.

## Alternatives Considered

- **Build registries / docs from scratch.** Rejected. The repo already has
  `ADOPTION_GATE.md` with a Decision Log table that is the right shape. Reusing
  existing infrastructure is cheaper and prevents parallel doc trees.
- **Replace existing tooling.** Rejected. `scripts/check_policy.py` is already a CI
  gate with mature behaviour around file presence and added-file detection. Extending
  it is much lower risk than introducing a new check.
- **Hardcode the api vocabulary list elsewhere** (config file, separate module).
  Rejected. Co-locating with `REQUIRED_FILES` and `KNOWN_SUBSYSTEM_DIRS` in the same
  script keeps the policy machinery in one place. The maintenance process is
  documented in `DEVELOPMENT_WORKFLOW.md`.
- **Auto-derive `LEGACY_API_VOCABULARY` from `/home/workspace/sematryx-api/`**
  at check time. Rejected — assumes CI runners have access to the api path
  (they don't; CI checks out engine only).
- **Make the substance check fire on docs as well as src.** Rejected. Docs are
  explicitly where the registry and audit ADRs need to discuss these terms.
  Scanning docs would force escape hatches (allow-lists, marker comments) that
  weaken the gate. Source-only scanning gives a clean, machine-checkable rule.
- **Add ablation verdicts as a hard release gate.** Considered. Deferred to a
  later PR; the current verdict rule (direction + significance) is good enough
  for evidence in the VR Substance Audit but isn't yet calibrated for
  block-or-ship decisions.

## Consequences

- **Positive:**
  - The CI policy job now mechanically catches "engine reproduced api vocabulary
    without porting substance." The topology drift could not have accumulated for
    6 weeks under this guard.
  - The Engine vs Legacy-API Registry is the canonical answer to "what's stub
    vs real?" — AI sessions and human reviewers consult one document.
  - The VR Substance Audit forces authors to explicitly state whether the
    implementation matches names and whether claims have behavioural backing.
    Authors cannot tick boxes without acknowledging the substance question.
  - The PRD Acceptance Shape forces authors to declare structural-only acceptance
    rather than implying behavioural acceptance that isn't being verified.
  - `CLAUDE.md` gives AI sessions a single grounding doc. Replaces the role
    `README.md` was incorrectly playing (and accumulating drift in).

- **Negative:**
  - Wider surface in `check_policy.py` (one new constant, one new check). Mitigated
    by source-only scanning (no doc scanning), word-boundary matching (no false
    positive substring matches), and the maintenance process documented in
    `DEVELOPMENT_WORKFLOW.md`.
  - `LEGACY_API_VOCABULARY` is hand-maintained; future audits will surface terms
    that need adding. Acceptable: each audit is a discrete event with a
    CHANGELOG entry.
  - Slightly heavier PR overhead: any PR adding api-derived vocabulary now requires
    a registry row. That's the point.

- **Follow-up tasks:**
  - Per-subsystem port/defer/drop decisions for the rows currently marked
    `decision needed` in the registry. Each decision becomes its own ADR or
    INTEGRATION_DEBT entry.
  - Rename or implement the remaining stubs flagged in the registry (contextual
    bandit, autodidactic loop, explanation, adaptation overlay). Apply the
    ADR-0026 pattern (rename + supersede + registry entry).
  - Calibrate an ablation-verdict-based release gate when there are enough ablation
    runs to set thresholds confidently.
  - Periodic audit cadence (quarterly or every 10 PRs) to catch new drift early.
    Tracked as INTEGRATION_DEBT entry until process is formalised.
