"""Stage 3 hybrid: outer exploration + discrete neighborhood refinement (end-to-end)."""

from __future__ import annotations

from sematryx_engine import optimize


def test_mixed_optimize_reaches_shell_optimum() -> None:
    def narrow_shell(x: list[float]) -> float:
        return (x[0] - 0.5) ** 2 + (x[1] - 1.0) ** 2

    result = optimize(
        objective_function=narrow_shell,
        variable_descriptors=[
            {"kind": "continuous", "low": 0.0, "high": 1.0},
            {"kind": "integer", "low": 0, "high": 2},
        ],
        max_evaluations=500,
        domain="stage3_hybrid_refinement_smoke",
        rng_seed=42,
    )
    assert result.success is True
    assert result.strategy_used == "hybrid_outer_random_inner_scipy"
    assert result.best_value < 0.1
    assert abs(result.best_solution[0] - 0.5) < 0.2
    assert abs(result.best_solution[1] - 1.0) < 0.6
