import pytest

from sematryx_engine import optimize


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_optimize_accepts_continuous_variable_descriptors() -> None:
    result = optimize(
        objective_function=sphere,
        variable_descriptors=[
            {"kind": "continuous", "low": -3.0, "high": 3.0},
            {"kind": "continuous", "low": -2.0, "high": 2.0},
        ],
        max_evaluations=300,
        domain="stage3_kickoff_continuous",
    )
    assert result.success is True
    assert len(result.best_solution) == 2


def test_optimize_integer_descriptors_uses_discrete_baseline() -> None:
    def shifted_sphere(x: list[float]) -> float:
        return sum((v - 5.0) ** 2 for v in x)

    result = optimize(
        objective_function=shifted_sphere,
        variable_descriptors=[
            {"kind": "integer", "low": 0, "high": 10},
            {"kind": "integer", "low": 0, "high": 10},
        ],
        max_evaluations=400,
        domain="stage3_discrete_integer",
    )
    assert result.success is True
    assert result.strategy_used == "discrete_random_neighborhood"
    assert len(result.best_solution) == 2
    assert all(abs(v - 5.0) < 1.5 for v in result.best_solution)


def test_optimize_categorical_prefers_expected_category() -> None:
    def pick_second(x: list[float]) -> float:
        idx = int(round(x[0]))
        return 0.0 if idx == 1 else 10.0 + float(idx)

    result = optimize(
        objective_function=pick_second,
        variable_descriptors=[
            {"kind": "categorical", "categories": ["a", "b", "c"]},
        ],
        max_evaluations=200,
        domain="stage3_discrete_categorical",
    )
    assert result.success is True
    assert int(round(result.best_solution[0])) == 1


def test_optimize_rejects_mixed_continuous_discrete() -> None:
    with pytest.raises(ValueError, match="hybrid routing"):
        optimize(
            objective_function=sphere,
            variable_descriptors=[
                {"kind": "continuous", "low": 0.0, "high": 1.0},
                {"kind": "integer", "low": 0, "high": 3},
            ],
            max_evaluations=50,
            domain="stage3_mixed_deferred",
        )
