# Incident Response

## Trigger Examples

### Runtime incidents

- Strategy quality regression over rolling windows
- Repeated policy gate failures
- Unexpected selection drift or unstable pass/fail behavior

### Documentation drift / substance audit (ADR-0027)

- Documented feature claims substantially exceed implementation substance — e.g.,
  names from the deprecated sematryx-api codebase reproduced in engine without an
  explicit port/defer/drop decision in the Engine vs Legacy-API Registry.
- README, SYSTEM_OVERVIEW, or PRDs accumulate marketing claims about behaviour that
  have no behavioural test or ablation verdict backing.
- An ablation verdict surfaces "feature X does not do what its name implies" or
  "claim X cannot be measured under any tested scenario."

## Procedure

### Runtime incidents

1. Freeze policy changes and keep last known good policy active.
2. Collect evidence: test outputs, benchmark deltas, recent PRs.
3. Run anomaly analysis and produce remediation proposal.
4. Validate proposal through deterministic gates.
5. Roll forward or roll back with documented rationale.

### Documentation drift / substance audit

1. Scope the audit: enumerate the affected subsystems and compare engine
   implementation against the legacy api reference where applicable.
2. Write a findings ADR (sibling pattern to ADR-0026, ADR-0027) documenting the
   gap between names and implementation, with concrete evidence (file paths, LOC
   ratios, missing machinery).
3. Update the Engine vs Legacy-API Registry in `docs/process/ADOPTION_GATE.md` with
   port/defer/drop decisions for each surfaced term.
4. Open a correction PR that renames stubs honestly (per ADR-0026 pattern),
   marks prior PRDs/ADRs superseded, and corrects the affected user-facing docs
   (README, SYSTEM_OVERVIEW). Add new terms to `LEGACY_API_VOCABULARY` in
   `scripts/check_policy.py` if a previously-unscanned term was involved.
5. Run the policy script locally and in CI to confirm the substance gate now
   guards against re-introduction.
