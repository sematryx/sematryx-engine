# Verification Report: Continuous Bandit Strategy Exclusions

## Reference

- PRD: `docs/prd/PRD-0021-continuous-bandit-strategy-exclusions.md`
- ADR(s): `docs/architecture/decisions/ADR-0020-continuous-bandit-strategy-exclusions.md`

## Planned vs Implemented

- [x] Continuous-only selector excludes discrete + hybrid strategies from bandit candidates.
  - Evidence: `src/sematryx_engine/engine/optimizer.py` (`select_with_basis` call in bounds-only path)
- [x] Regression coverage for `strategy_used` on a bounds-only optimize call.
  - Evidence: `tests/integration/test_continuous_bandit_excludes_hybrid_strategies.py`

## Commands Run

```bash
uv run --extra dev ruff check src tests scripts
uv run --extra dev mypy src
uv run --extra dev pytest --import-mode=importlib
uv run python scripts/check_policy.py
```

## Deviations

None.

## Shortcut Audit

- [x] No runtime mocks/stubs used where real integration was required.
- [x] No forbidden imports introduced.
- [x] No acceptance criteria skipped.
