# Verification Report: <Feature Name>

## Reference

- PRD: `docs/prd/<PRD-file>.md`
- ADR(s): `docs/architecture/decisions/<ADR-files>.md`

## Planned vs Implemented

For each PRD acceptance criterion, provide evidence:

- [ ] Criterion 1 -> evidence (test name, output, file path)
- [ ] Criterion 2 -> evidence (test name, output, file path)
- [ ] Criterion 3 -> evidence (test name, output, file path)

## Commands Run

```bash
make all
python -m pytest tests/integration
```

## Deviations

Document any deviation from the PRD/ADR and why.

## Shortcut Audit

- [ ] No runtime path uses mocks/stubs where real engine integration was required
- [ ] No forbidden imports introduced
- [ ] No acceptance criteria skipped

## Substance Audit (ADR-0027)

- [ ] Implementation matches what names imply — no inherited vocabulary from the deprecated
      sematryx-api codebase without an explicit port/defer/drop decision recorded in the
      Engine vs Legacy-API Registry in `docs/process/ADOPTION_GATE.md`.
- [ ] Doc claims about behavior have a behavioral test or ablation verdict — or are explicitly
      marked `[STUB]`/`[ASPIRATIONAL]` in the README/SYSTEM_OVERVIEW.
- [ ] If the PRD acceptance criteria are structural only (file exists, field present),
      the Acceptance Shape section of the PRD calls that out explicitly.
