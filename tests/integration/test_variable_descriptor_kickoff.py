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


def test_optimize_rejects_integer_descriptors_until_solver_slice() -> None:
    with pytest.raises(ValueError):
        optimize(
            objective_function=sphere,
            variable_descriptors=[
                {"kind": "integer", "low": 0, "high": 10},
            ],
            max_evaluations=100,
            domain="stage3_kickoff_integer",
        )
