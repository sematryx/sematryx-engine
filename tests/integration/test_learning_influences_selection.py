from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def test_learning_history_can_override_cold_start_selection(tmp_path: Path) -> None:
    # Ensures historical local evidence can deterministically influence selection.
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")
    selector = StrategySelector(memory=memory)

    for _ in range(4):
        memory.store_optimization_result(
            strategy_name="scipy_de",
            domain="general",
            problem_features={"dimensions": 6},
            performance_metrics={
                "final_value": 0.1,
                "iterations": 30,
                "time": 0.2,
                "success": True,
            },
        )

    features = extract_problem_features(
        bounds=[(-5.0, 5.0)] * 6,
        max_evaluations=300,
    )
    strategy, confidence = selector.select(features=features, domain="general")

    assert strategy == "scipy_de"
    assert confidence >= 0.9
