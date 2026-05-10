# Verification Report: Stage 3 Hybrid Routing

## Reference

- PRD: `docs/prd/PRD-0018-stage3-hybrid-routing.md`
- ADR(s): `docs/architecture/decisions/ADR-0017-stage3-hybrid-routing.md`

## Planned vs Implemented

- [x] Mixed encoded bounds + `normalize_mixed_solution` for full-vector validity.
  - Evidence: `src/sematryx_engine/api/variable_descriptors.py`
- [x] Hybrid solver `solve_hybrid_outer_random_inner_scipy` with budget splitting.
  - Evidence: `src/sematryx_engine/solvers/hybrid_solvers.py`
- [x] Optimizer + client routing; inner strategy `exclude_strategies` on selector.
  - Evidence: `src/sematryx_engine/engine/optimizer.py`, `src/sematryx_engine/api/client.py`, `src/sematryx_engine/engine/strategy_selector.py`
- [x] Tests.
  - Evidence: `tests/unit/test_hybrid_solvers.py`, `tests/integration/test_variable_descriptor_kickoff.py`

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
