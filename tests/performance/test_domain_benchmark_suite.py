import random
from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def _run_selection_benchmark(
    *,
    domain: str,
    bounds: list[tuple[float, float]],
    max_evaluations: int,
    warm_strategy: str | None,
    warm_count: int,
    runs: int,
    tmp_path: Path,
) -> tuple[float, float]:
    memory = LocalStrategyMemory(tmp_path / f"{domain}_memory.db")
    if warm_strategy is not None:
        for _ in range(warm_count):
            memory.store_optimization_result(
                strategy_name=warm_strategy,
                domain=domain,
                problem_features={"dimensions": len(bounds)},
                performance_metrics={
                    "final_value": 0.02,
                    "iterations": 50,
                    "time": 0.2,
                    "success": True,
                },
            )

    selector = StrategySelector(memory=memory)
    features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)

    target_hits = 0
    confidence_sum = 0.0
    for _ in range(runs):
        strategy, confidence = selector.select(features=features, domain=domain)
        confidence_sum += confidence
        if warm_strategy is not None and strategy == warm_strategy:
            target_hits += 1

    hit_rate = (target_hits / runs) if warm_strategy is not None else 0.0
    mean_confidence = confidence_sum / runs
    return hit_rate, mean_confidence


def test_domain_benchmark_rugged_warm_vs_cold(tmp_path: Path) -> None:
    random.seed(21)
    cold_hit_rate, cold_confidence = _run_selection_benchmark(
        domain="rugged_search",
        bounds=[(-9.0, 9.0)] * 6,
        max_evaluations=300,
        warm_strategy=None,
        warm_count=0,
        runs=100,
        tmp_path=tmp_path,
    )
    warm_hit_rate, warm_confidence = _run_selection_benchmark(
        domain="rugged_search",
        bounds=[(-9.0, 9.0)] * 6,
        max_evaluations=300,
        warm_strategy="scipy_de",
        warm_count=8,
        runs=100,
        tmp_path=tmp_path,
    )

    assert cold_hit_rate == 0.0
    assert 0.2 <= cold_confidence <= 0.8
    assert warm_hit_rate >= 0.95
    assert warm_confidence >= 0.9


def test_domain_benchmark_high_dimensional_warm_vs_cold(tmp_path: Path) -> None:
    random.seed(37)
    cold_hit_rate, cold_confidence = _run_selection_benchmark(
        domain="high_dimensional",
        bounds=[(-5.0, 5.0)] * 18,
        max_evaluations=350,
        warm_strategy=None,
        warm_count=0,
        runs=100,
        tmp_path=tmp_path,
    )
    warm_hit_rate, warm_confidence = _run_selection_benchmark(
        domain="high_dimensional",
        bounds=[(-5.0, 5.0)] * 18,
        max_evaluations=350,
        warm_strategy="scipy_dual_annealing",
        warm_count=8,
        runs=100,
        tmp_path=tmp_path,
    )

    assert cold_hit_rate == 0.0
    assert 0.2 <= cold_confidence <= 0.8
    assert warm_hit_rate >= 0.95
    assert warm_confidence >= 0.9
