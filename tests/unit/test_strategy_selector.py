from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def test_selector_uses_memory_override_with_sufficient_history(tmp_path: Path) -> None:
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")
    selector = StrategySelector(memory=memory)

    for _ in range(3):
        memory.store_optimization_result(
            strategy_name="scipy_dual_annealing",
            domain="general",
            problem_features={"dimensions": 4},
            performance_metrics={
                "final_value": 0.2,
                "iterations": 20,
                "time": 0.1,
                "success": True,
            },
        )

    features = extract_problem_features(
        bounds=[(-2.0, 2.0)] * 4,
        max_evaluations=200,
    )
    strategy, confidence = selector.select(features=features, domain="general")

    assert strategy == "scipy_dual_annealing"
    assert confidence == 0.9
