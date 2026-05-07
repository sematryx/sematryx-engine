from sematryx_engine import optimize


def test_optimize_smoke() -> None:
    def sphere(x: list[float]) -> float:
        return sum(v * v for v in x)

    result = optimize(
        objective_function=sphere,
        bounds=[(-1.0, 1.0), (-2.0, 2.0)],
        max_evaluations=10,
    )

    assert result.success is True
    assert len(result.best_solution) == 2
    assert result.evaluations >= 1
    assert result.strategy_used in {
        "scipy_de",
        "scipy_dual_annealing",
        "scipy_local_lbfgsb",
    }
