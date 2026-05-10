"""Stage 3 acceptance (criterion 3): discrete-shaped domains warm toward discrete_capable strategy."""

from pathlib import Path

from sematryx_engine.engine.benchmark_metrics import run_selection_benchmark


def test_discrete_knapsack_shaped_memory_raises_confidence_and_hit_rate(tmp_path: Path) -> None:
    cold = run_selection_benchmark(
        domain="stage3_accept_knapsack",
        bounds=[(0.0, 1.0)] * 4,
        max_evaluations=500,
        warm_strategy=None,
        warm_count=0,
        runs=60,
        memory_path=tmp_path / "knapsack_cold.db",
    )
    warm = run_selection_benchmark(
        domain="stage3_accept_knapsack",
        bounds=[(0.0, 1.0)] * 4,
        max_evaluations=500,
        warm_strategy="discrete_random_neighborhood",
        warm_count=8,
        runs=60,
        memory_path=tmp_path / "knapsack_warm.db",
    )
    assert warm.hit_rate >= 0.95
    assert warm.mean_confidence > cold.mean_confidence + 0.05


def test_discrete_assignment_shaped_memory_raises_confidence_and_hit_rate(tmp_path: Path) -> None:
    cold = run_selection_benchmark(
        domain="stage3_accept_assignment2x2",
        bounds=[(0.0, 1.0)] * 2,
        max_evaluations=400,
        warm_strategy=None,
        warm_count=0,
        runs=60,
        memory_path=tmp_path / "assign_cold.db",
    )
    warm = run_selection_benchmark(
        domain="stage3_accept_assignment2x2",
        bounds=[(0.0, 1.0)] * 2,
        max_evaluations=400,
        warm_strategy="discrete_random_neighborhood",
        warm_count=8,
        runs=60,
        memory_path=tmp_path / "assign_warm.db",
    )
    assert warm.hit_rate >= 0.95
    assert warm.mean_confidence > cold.mean_confidence + 0.05
