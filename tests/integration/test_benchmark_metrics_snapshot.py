"""Integration: benchmark snapshot matches performance suite expectations."""

from pathlib import Path

from sematryx_engine.engine.benchmark_metrics import collect_domain_benchmark_snapshot


def test_collect_domain_benchmark_snapshot_thresholds(tmp_path: Path) -> None:
    payload = collect_domain_benchmark_snapshot(tmp_path=tmp_path)
    scenarios = payload["scenarios"]
    assert isinstance(scenarios, dict)

    rugged = scenarios["rugged_search"]
    assert rugged["cold"]["hit_rate"] == 0.0
    assert rugged["warm"]["hit_rate"] >= 0.95
    assert rugged["warm"]["mean_confidence"] >= 0.9

    hd = scenarios["high_dimensional"]
    assert hd["cold"]["hit_rate"] == 0.0
    assert hd["warm"]["hit_rate"] >= 0.95
    assert hd["warm"]["mean_confidence"] >= 0.9
