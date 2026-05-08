from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import (
    StrategySelector,
    memory_override_confidence,
)
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


def test_memory_override_confidence_curve() -> None:
    assert memory_override_confidence(2) == 0.0
    assert memory_override_confidence(3) == 0.9
    assert memory_override_confidence(8) == 0.95
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


def test_selector_prefers_tunneling_when_physarum_signal_is_aggressive(tmp_path: Path) -> None:
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")
    selector = StrategySelector(memory=memory)
    features = extract_problem_features(bounds=[(-8.0, 8.0)] * 6, max_evaluations=120)

    strategy, confidence, basis = selector.select_with_basis(
        features=features,
        domain="general",
        topology_artifact={
            "physarum_tunneling_score": 0.91,
            "tunneling_directive": "aggressive",
        },
    )

    assert strategy == "scipy_dual_annealing"
    assert confidence == 0.86
    assert basis == "physarum_tunneling_override"
