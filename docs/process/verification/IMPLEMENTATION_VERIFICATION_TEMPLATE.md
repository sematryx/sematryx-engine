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
