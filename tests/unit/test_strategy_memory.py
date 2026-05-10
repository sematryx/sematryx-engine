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


def test_strategy_memory_descriptor_mix_filter(tmp_path: Path) -> None:
    memory = LocalStrategyMemory(tmp_path / "scoped.db")
    domain = "scoped_domain"
    base_feat = {"dimensions": 2}

    for _ in range(3):
        memory.store_optimization_result(
            strategy_name="scipy_de",
            domain=domain,
            problem_features=base_feat,
            performance_metrics={
                "final_value": 0.001,
                "iterations": 10,
                "time": 0.01,
                "success": True,
            },
        )

    for _ in range(3):
        memory.store_optimization_result(
            strategy_name="scipy_shgo",
            domain=domain,
            problem_features={**base_feat, "descriptor_mix": "discrete_only"},
            performance_metrics={
                "final_value": 0.5,
                "iterations": 20,
                "time": 0.02,
                "success": True,
            },
        )

    rec_discrete = memory.get_strategy_recommendations(
        domain=domain,
        descriptor_mix="discrete_only",
    )
    assert len(rec_discrete) >= 1
    assert rec_discrete[0].strategy_name == "scipy_shgo"

    rec_all = memory.get_strategy_recommendations(domain=domain)
    assert rec_all[0].strategy_name == "scipy_de"
