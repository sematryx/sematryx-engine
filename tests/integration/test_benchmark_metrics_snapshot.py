"""Integration: benchmark snapshot matches performance suite expectations."""

from pathlib import Path

from sematryx_engine.engine.benchmark_metrics import collect_domain_benchmark_snapshot


def test_collect_domain_benchmark_snapshot_thresholds(tmp_path: Path) -> None:
    payload = collect_domain_benchmark_snapshot(tmp_path=tmp_path)
    assert payload["version"] == 2
    scenarios = payload["scenarios"]
    objectives = payload["objectives"]
    assert isinstance(scenarios, dict)
    assert isinstance(objectives, dict)

    rugged = scenarios["rugged_search"]
    assert rugged["cold"]["hit_rate"] == 0.0
    assert rugged["warm"]["hit_rate"] >= 0.95
    assert rugged["warm"]["mean_confidence"] >= 0.9

    hd = scenarios["high_dimensional"]
    assert hd["cold"]["hit_rate"] == 0.0
    assert hd["warm"]["hit_rate"] >= 0.95
    assert hd["warm"]["mean_confidence"] >= 0.9

    dk = scenarios["discrete_knapsack"]
    assert dk["warm"]["hit_rate"] >= 0.95
    assert dk["warm"]["mean_confidence"] >= 0.9
    assert dk["warm"]["mean_confidence"] > dk["cold"]["mean_confidence"]

    da = scenarios["discrete_assignment2x2"]
    assert da["warm"]["hit_rate"] >= 0.95
    assert da["warm"]["mean_confidence"] >= 0.9
    assert da["warm"]["mean_confidence"] > da["cold"]["mean_confidence"]

    sphere4 = objectives["sphere_dim4"]
    sphere8 = objectives["sphere_dim8"]
    assert float(sphere4["best_value"]) < 0.2
    assert float(sphere8["best_value"]) < 5.0
    assert float(objectives["knapsack01"]["best_value"]) <= -9.99
    assert float(objectives["assignment2x2"]["best_value"]) <= 3.01
