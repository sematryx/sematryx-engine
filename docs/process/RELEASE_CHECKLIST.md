# Release Checklist

- [ ] `make all` passes
- [ ] `pytest tests/integration` passes
- [ ] PRD and verification report are complete
- [ ] ADR updates merged for architecture changes
- [ ] CHANGELOG updated
- [ ] INTEGRATION_DEBT updated
- [ ] Branch protection and required checks enabled
- [ ] Rollback plan documented in PR

## Branch Protection Verification Notes

- Protected branch: `main`
- Required status check: `CI / test`
- Pull requests required before merge
- Force pushes and branch deletion disabled
