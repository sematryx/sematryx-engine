"""Regression: bounds-only optimize must not dispatch descriptor-shaped strategies."""

from __future__ import annotations

from sematryx_engine.api.client import optimize


def _sphere(xs: list[float]) -> float:
    return sum(x * x for x in xs)


def test_continuous_optimize_never_selects_discrete_or_hybrid_arms() -> None:
    result = optimize(
        objective_function=_sphere,
        bounds=[(-2.0, 2.0)] * 4,
        max_evaluations=400,
        domain="general",
    )
    assert result.strategy_used != "hybrid_outer_random_inner_scipy"
    assert result.strategy_used != "discrete_random_neighborhood"
