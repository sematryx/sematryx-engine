# Release Checklist

- [ ] `make all` passes
- [ ] `CI / required-checks` is green (includes `integration-performance`: `pytest tests/integration tests/performance --import-mode=importlib`)
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

GitHub lists each job as `CI / <job name>`. Parallel jobs: `lint`, `typecheck`, `unit-smoke`,
`integration-performance`, `policy`.
Configure branch protection so **only** `CI / required-checks` is required (it `needs` the five leaf jobs above);
this keeps one merge gate while preserving parallel runs. Optionally add those leaf jobs as required too
for stricter visibility.
