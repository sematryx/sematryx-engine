# Definition Of Done

A change is done only if all items below are satisfied.

## Mandatory Gates

- [ ] `ruff check src tests scripts` passes
- [ ] `mypy src` passes
- [ ] `pytest tests/unit tests/smoke` passes
- [ ] Policy checks pass: `python scripts/check_policy.py`
- [ ] Forbidden import checks pass: `python scripts/check_forbidden_imports.py`

## Change Artifacts

- [ ] Tests were added/updated for behavior changes
- [ ] README updated when user-visible behavior changed
- [ ] ADR added/updated for architecture-impacting changes
- [ ] PRD added/updated for source-code changes
- [ ] Verification report added/updated under `docs/process/verification/`
- [ ] PR includes risk and rollback notes

## Substance Gates (ADR-0027)

- [ ] Implementation matches what names imply. If code introduces vocabulary from the
      deprecated sematryx-api codebase (see `LEGACY_API_VOCABULARY` in
      `scripts/check_policy.py`), the Engine vs Legacy-API Registry in
      `docs/process/ADOPTION_GATE.md` records an explicit port/defer/drop decision.
- [ ] Doc claims about feature behaviour have backing — a behavioural test, an
      ablation verdict, or an explicit `[STUB]`/`[ASPIRATIONAL]` marker. The VR's
      Substance Audit section is filled honestly, not ceremonially.
- [ ] PRD Acceptance Shape declared. If all acceptance criteria are structural
      (file exists, field present, function callable), the PRD says so explicitly.
      At least one behavioural criterion is required for any feature claiming
      user-facing value.

## Review

- [ ] Code review complete and concerns resolved
- [ ] No unresolved TODOs for core behavior paths
