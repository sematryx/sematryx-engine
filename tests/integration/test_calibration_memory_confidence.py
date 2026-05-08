"""Integration: memory override confidence scales with historical usage."""

from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector, memory_override_confidence
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def test_memory_override_confidence_increases_with_usage(tmp_path: Path) -> None:
    features = extract_problem_features(
        bounds=[(-2.0, 2.0)] * 4,
        max_evaluations=200,
    )

    for n in (3, 8):
        db_path = tmp_path / f"mem_{n}.db"
        mem = LocalStrategyMemory(db_path)
        for _ in range(n):
            mem.store_optimization_result(
                strategy_name="scipy_de",
                domain="scaling_domain",
                problem_features={"dimensions": 4},
                performance_metrics={
                    "final_value": 0.05,
                    "iterations": 30,
                    "time": 0.1,
                    "success": True,
                },
            )
        selector = StrategySelector(memory=mem)
        _strategy, conf = selector.select(features=features, domain="scaling_domain")
        assert conf == memory_override_confidence(n)

    assert memory_override_confidence(8) > memory_override_confidence(3)
