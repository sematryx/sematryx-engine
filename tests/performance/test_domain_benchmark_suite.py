import random
from pathlib import Path

from sematryx_engine.engine.benchmark_metrics import (
    SelectionBenchmarkResult,
    run_selection_benchmark,
)


def test_domain_benchmark_rugged_warm_vs_cold(tmp_path: Path) -> None:
    random.seed(21)
    cold_hit_rate, cold_confidence = _metrics(
        run_selection_benchmark(
            domain="rugged_search",
            bounds=[(-9.0, 9.0)] * 6,
            max_evaluations=300,
            warm_strategy=None,
            warm_count=0,
            runs=100,
            memory_path=tmp_path / "rugged_cold.db",
        )
    )
    warm_hit_rate, warm_confidence = _metrics(
        run_selection_benchmark(
            domain="rugged_search",
            bounds=[(-9.0, 9.0)] * 6,
            max_evaluations=300,
            warm_strategy="scipy_de",
            warm_count=8,
            runs=100,
            memory_path=tmp_path / "rugged_warm.db",
        )
    )

    assert cold_hit_rate == 0.0
    assert 0.2 <= cold_confidence <= 0.8
    assert warm_hit_rate >= 0.95
    assert warm_confidence >= 0.9


def test_domain_benchmark_high_dimensional_warm_vs_cold(tmp_path: Path) -> None:
    random.seed(37)
    cold_hit_rate, cold_confidence = _metrics(
        run_selection_benchmark(
            domain="high_dimensional",
            bounds=[(-5.0, 5.0)] * 18,
            max_evaluations=350,
            warm_strategy=None,
            warm_count=0,
            runs=100,
            memory_path=tmp_path / "hd_cold.db",
        )
    )
    warm_hit_rate, warm_confidence = _metrics(
        run_selection_benchmark(
            domain="high_dimensional",
            bounds=[(-5.0, 5.0)] * 18,
            max_evaluations=350,
            warm_strategy="scipy_dual_annealing",
            warm_count=8,
            runs=100,
            memory_path=tmp_path / "hd_warm.db",
        )
    )

    assert cold_hit_rate == 0.0
    assert 0.2 <= cold_confidence <= 0.8
    assert warm_hit_rate >= 0.95
    assert warm_confidence >= 0.9


def _metrics(result: SelectionBenchmarkResult) -> tuple[float, float]:
    return result.hit_rate, result.mean_confidence
