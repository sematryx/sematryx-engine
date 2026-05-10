# Development Workflow

This repository follows a rigid, enforced workflow.

## Required Sequence

1. Skim `docs/planning/ACTIVE_PLAN.md` for current slice ordering; adjust when priorities change (same PR when practical).
2. Define outcome, constraints, and non-goals (PRD/issue scope)
3. Create/update ADR for architecture-impacting decisions
4. Implement in small vertical slices
5. Add/update tests in the same slice
6. Write verification report mapping PRD criteria to evidence
7. Run quality + policy checks locally
8. Open PR using the repository template
9. Address review feedback
10. Merge only when all checks are green

## Enforcement

- Pre-commit hooks run lint, typing, tests, and policy checks.
- Policy scripts block merges when required artifacts are missing.
- CI runs `check_release_checklist.py` to prevent release checklist drift.
- Forbidden imports are blocked for cloud/platform packages in local-first core.
- PRD and verification artifacts are mandatory for source-code changes.
- Strict mode: source changes must include NEW `PRD-*.md` and NEW `VR-*.md` files.
- Strict mode: changes under engine/learning/solvers must include a NEW ADR file.
- New subsystem directories require an adoption-gate update with trial evidence.

## Adoption Gate

Before integrating any candidate subsystem/module, complete the gate in
`docs/process/ADOPTION_GATE.md` and record go/no-go evidence.

## Branch Protection Verification

Before relying on guardrails, confirm GitHub branch protection for `main` includes:

- Require a pull request before merging
- Require status checks to pass with `CI / required-checks`
- Require branches to be up to date before merging
- Block force pushes and deletions

### CI job names (multi-job workflow)

Workflow file: `.github/workflows/ci.yml`. Status checks appear as:

| Check name | Purpose |
|------------|---------|
| `CI / lint` | Ruff on `src`, `tests`, `scripts` |
| `CI / typecheck` | Mypy on `src` |
| `CI / unit-smoke` | `pytest tests/unit tests/smoke` |
| `CI / integration-performance` | `pytest tests/integration tests/performance --import-mode=importlib` |
| `CI / policy` | Forbidden imports, policy, release checklist scripts |
| `CI / required-checks` | Passes only if all of the above succeed |

**Branch rule:** set the required check to `CI / required-checks` so a single green gate implies the
full matrix passed. After changing workflow job IDs, update this table and `RELEASE_CHECKLIST.md`, then
align the protected branch’s required check name in GitHub settings.

## Local Commands

```bash
.venv311/bin/python -m pip install -e ".[dev]"
.venv311/bin/python -m ruff check src tests scripts
.venv311/bin/python -m mypy src
.venv311/bin/python -m pytest tests/unit tests/smoke
.venv311/bin/python -m pytest tests/integration tests/performance --import-mode=importlib
.venv311/bin/python scripts/check_forbidden_imports.py
.venv311/bin/python scripts/check_policy.py
```
