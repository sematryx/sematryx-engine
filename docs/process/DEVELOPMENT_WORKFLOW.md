# Development Workflow

This repository follows a rigid, enforced workflow.

## Required Sequence

1. Define outcome, constraints, and non-goals (PRD/issue scope)
2. Create/update ADR for architecture-impacting decisions
3. Implement in small vertical slices
4. Add/update tests in the same slice
5. Write verification report mapping PRD criteria to evidence
6. Run quality + policy checks locally
7. Open PR using the repository template
8. Address review feedback
9. Merge only when all checks are green

## Enforcement

- Pre-commit hooks run lint, typing, tests, and policy checks.
- Policy scripts block merges when required artifacts are missing.
- Forbidden imports are blocked for cloud/platform packages in local-first core.
- PRD and verification artifacts are mandatory for source-code changes.

## Local Commands

```bash
.venv311/bin/python -m pip install -e ".[dev]"
.venv311/bin/python -m ruff check src tests scripts
.venv311/bin/python -m mypy src
.venv311/bin/python -m pytest tests/unit tests/smoke
.venv311/bin/python scripts/check_forbidden_imports.py
.venv311/bin/python scripts/check_policy.py
```
