"""Objective-quality benchmarks beyond strategy selection hit-rate."""

from pathlib import Path

from sematryx_engine.engine.benchmark_metrics import (
    collect_objective_benchmark_snapshot,
    run_objective_benchmark_isolated,
    sphere_objective,
)


def test_sphere_objective_is_near_optimum_small_problem(tmp_path: Path) -> None:
    result = run_objective_benchmark_isolated(
        scenario_name="sphere_dim4",
        bounds=[(-5.0, 5.0)] * 4,
        max_evaluations=400,
        domain="obj_quality_small",
        memory_path=tmp_path / "m.db",
        bandit_state_path=tmp_path / "b.json",
        objective_seed=101,
    )
    assert result.evaluations >= 1
    assert result.best_value < 0.2


def test_sphere_objective_reasonable_mid_problem(tmp_path: Path) -> None:
    result = run_objective_benchmark_isolated(
        scenario_name="sphere_dim8",
        bounds=[(-4.0, 4.0)] * 8,
        max_evaluations=600,
        domain="obj_quality_mid",
        memory_path=tmp_path / "m2.db",
        bandit_state_path=tmp_path / "b2.json",
        objective_seed=103,
    )
    assert result.evaluations >= 1
    assert result.best_value < 5.0


def test_collect_objective_snapshot_matches_standalone_rows(tmp_path: Path) -> None:
    snap = collect_objective_benchmark_snapshot(tmp_path)
    assert set(snap.keys()) == {"sphere_dim4", "sphere_dim8"}
    row4 = snap["sphere_dim4"]
    assert isinstance(row4, dict)
    assert float(row4["best_value"]) < 0.2


def test_sphere_objective_function_contract() -> None:
    assert sphere_objective([1.0, -2.0]) == 5.0
