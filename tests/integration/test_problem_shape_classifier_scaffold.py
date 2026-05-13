from sematryx_engine import optimize
from sematryx_engine.engine.strategy_selector import STRATEGIES


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_optimize_includes_problem_shape() -> None:
    result = optimize(
        objective_function=sphere,
        bounds=[(-3.0, 3.0), (-1.0, 1.0), (-2.0, 2.0)],
        max_evaluations=120,
        domain="problem_shape_scaffold",
    )

    assert result.success is True
    assert len(result.best_solution) == 3
    assert result.strategy_used in STRATEGIES
    assert result.problem_shape is not None
    artifact = result.problem_shape
    assert artifact["version"] == 2
    assert artifact["dimensions"] == 3
    assert artifact["budget_regime"] == "tight"
    assert artifact["complexity_hint"] in {"low", "medium", "high"}
    assert artifact["shape_routing_directive"] in {"local", "balanced", "aggressive"}
    assert result.explanation is not None
    assert result.explanation["strategy_used"] == result.strategy_used
    assert result.explanation["selection_basis"] in {
        "bandit",
        "memory_override",
        "shape_routing_override",
    }


def test_optimize_autodidactic_attempt_loop_records_attempts() -> None:
    result = optimize(
        objective_function=sphere,
        bounds=[(-5.0, 5.0), (-5.0, 5.0)],
        max_evaluations=900,
        domain="autodidactic_loop",
    )
    assert result.explanation is not None
    assert result.explanation["attempt_limit"] == 3
    attempts = result.explanation["attempts"]
    assert isinstance(attempts, list)
    assert len(attempts) == 3
    for row in attempts:
        assert row["strategy"]
        assert float(row["best_value"]) >= 0.0
