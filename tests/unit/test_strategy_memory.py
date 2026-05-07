from pathlib import Path

from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def test_strategy_memory_store_and_recommend(tmp_path: Path) -> None:
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")

    memory.store_optimization_result(
        strategy_name="scipy_de",
        domain="general",
        problem_features={"dimensions": 2},
        performance_metrics={"final_value": 1.0, "iterations": 20, "time": 0.1, "success": True},
    )
    memory.store_optimization_result(
        strategy_name="scipy_local_lbfgsb",
        domain="general",
        problem_features={"dimensions": 2},
        performance_metrics={"final_value": 0.5, "iterations": 15, "time": 0.05, "success": True},
    )

    recommendations = memory.get_strategy_recommendations(domain="general")
    assert len(recommendations) >= 2
    assert recommendations[0].strategy_name == "scipy_local_lbfgsb"
