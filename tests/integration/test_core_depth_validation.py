from pathlib import Path

from sematryx_engine import optimize
from sematryx_engine.engine.benchmark_metrics import collect_domain_benchmark_snapshot
from sematryx_engine.engine.strategy_selector import STRATEGIES


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_core_depth_validation_snapshot_and_runtime_contract(tmp_path: Path) -> None:
    snapshot = collect_domain_benchmark_snapshot(tmp_path=tmp_path)
    assert snapshot["version"] == 2
    objectives = snapshot["objectives"]
    assert float(objectives["sphere_dim4"]["best_value"]) < 0.2
    assert float(objectives["sphere_dim8"]["best_value"]) < 5.0

    result = optimize(
        objective_function=sphere,
        bounds=[(-5.0, 5.0)] * 6,
        max_evaluations=900,
        domain="core_depth_validation",
    )
    assert result.success is True
    assert result.strategy_used in STRATEGIES

    shape = result.problem_shape
    assert shape is not None
    assert shape["version"] == 2
    assert shape["shape_routing_directive"] in {"local", "balanced", "aggressive"}

    expl = result.explanation
    assert expl is not None
    assert expl["selection_basis"] in {"bandit", "memory_override", "shape_routing_override"}
    assert isinstance(expl["tuning_priors"], dict)

    attempts = expl["attempts"]
    assert isinstance(attempts, list)
    assert len(attempts) == int(expl["attempt_limit"])
    assert all(int(row["budget_allocated"]) >= 20 for row in attempts)

    adaptation = expl["adaptation"]
    assert isinstance(adaptation, dict)
    assert adaptation["planned_strategies"]
    assert len(adaptation["planned_strategies"]) == int(expl["attempt_limit"])
    winner = int(adaptation["winning_attempt"])
    assert 1 <= winner <= int(expl["attempt_limit"])
