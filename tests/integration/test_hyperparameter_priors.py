from sematryx_engine import optimize


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_optimize_explanation_includes_tuning_priors() -> None:
    result = optimize(
        objective_function=sphere,
        bounds=[(-3.0, 3.0)] * 4,
        max_evaluations=500,
        domain="hyperparameter_priors_integration",
    )
    assert result.explanation is not None
    priors = result.explanation["tuning_priors"]
    assert isinstance(priors, dict)
    assert priors["version"] == 1
    attempts = result.explanation["attempts"]
    assert isinstance(attempts, list)
    assert all("budget_allocated" in row for row in attempts)
