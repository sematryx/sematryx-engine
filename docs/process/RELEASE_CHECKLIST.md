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
- Required status check: `CI / required-checks` (aggregate gate; see `Development Workflow` for job names)
- Pull requests required before merge
- Force pushes and branch deletion disabled

### Multi-job CI

GitHub lists each job as `CI / <job name>`. Parallel jobs: `lint`, `typecheck`, `unit-smoke`, `policy`.
Configure branch protection so **only** `CI / required-checks` is required (it `needs` the four jobs above);
this keeps one merge gate while preserving parallel runs. Optionally add the four jobs as required too
for stricter visibility—then all five must pass.
