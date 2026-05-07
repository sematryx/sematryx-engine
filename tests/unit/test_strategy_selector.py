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


def test_selector_deterministic_bandit_mode(tmp_path: Path) -> None:
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")
    selector = StrategySelector(memory=memory)
    for _ in range(10):
        selector.update("scipy_de", 1.0)
    for _ in range(3):
        selector.update("scipy_local_lbfgsb", 0.0)

    features = extract_problem_features(
        bounds=[(-3.0, 3.0)] * 8,
        max_evaluations=300,
    )
    strategy, _ = selector.select(
        features=features,
        domain="general",
        deterministic_bandit=True,
    )
    assert strategy == "scipy_de"
