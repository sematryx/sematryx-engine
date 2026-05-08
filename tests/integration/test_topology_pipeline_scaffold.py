from sematryx_engine import optimize


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_optimize_includes_topology_artifact() -> None:
    result = optimize(
        objective_function=sphere,
        bounds=[(-3.0, 3.0), (-1.0, 1.0), (-2.0, 2.0)],
        max_evaluations=120,
        domain="topology_scaffold",
    )

    assert result.success is True
    assert len(result.best_solution) == 3
    assert result.strategy_used
    assert result.topology_artifact is not None
    artifact = result.topology_artifact
    assert artifact["version"] == 1
    assert artifact["dimensions"] == 3
    assert artifact["budget_regime"] == "tight"
    assert artifact["complexity_hint"] in {"low", "medium", "high"}
