import random
from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory

TARGET_STRATEGY = "scipy_de"


def _selection_hit_rate(selector: StrategySelector, domain: str, runs: int = 60) -> float:
    hits = 0
    features = extract_problem_features(
        bounds=[(-10.0, 10.0)] * 6,
        max_evaluations=300,
    )
    for _ in range(runs):
        strategy, _ = selector.select(features=features, domain=domain)
        if strategy == TARGET_STRATEGY:
            hits += 1
    return hits / runs


def test_warm_domain_memory_improves_repeated_selection_quality(tmp_path: Path) -> None:
    random.seed(42)
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")
    cold_selector = StrategySelector(memory=memory)

    cold_rate = _selection_hit_rate(
        selector=cold_selector,
        domain="manufacturing",
        runs=80,
    )

    for _ in range(8):
        memory.store_optimization_result(
            strategy_name=TARGET_STRATEGY,
            domain="manufacturing",
            problem_features={"dimensions": 6},
            performance_metrics={
                "final_value": 0.02,
                "iterations": 40,
                "time": 0.15,
                "success": True,
            },
        )

    warm_selector = StrategySelector(memory=memory)
    warm_rate = _selection_hit_rate(
        selector=warm_selector,
        domain="manufacturing",
        runs=80,
    )

    assert warm_rate >= 0.95
    assert warm_rate > cold_rate
