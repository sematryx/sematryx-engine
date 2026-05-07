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

## Review

- [ ] Code review complete and concerns resolved
- [ ] No unresolved TODOs for core behavior paths
