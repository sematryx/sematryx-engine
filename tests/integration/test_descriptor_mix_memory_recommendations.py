"""Hybrid inner selection uses descriptor_mix-scoped memory when available."""

from __future__ import annotations

from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def test_hybrid_inner_memory_prefers_mix_scoped_history(tmp_path: Path) -> None:
    """Rows without descriptor_mix must not dominate inner picks for mixed-shaped recall."""
    memory = LocalStrategyMemory(tmp_path / "mix_memory.db")
    domain = "stage3_mix_scope_demo"
    _blend = {
        "dimensions": 4,
        "avg_range": 2.0,
        "bounded": True,
        "budget_per_dimension": 125.0,
        "complexity": "medium",
    }

    for _ in range(4):
        memory.store_optimization_result(
            strategy_name="scipy_de",
            domain=domain,
            problem_features={**_blend},
            performance_metrics={
                "final_value": 0.001,
                "iterations": 80,
                "time": 0.1,
                "success": True,
            },
        )

    for _ in range(4):
        memory.store_optimization_result(
            strategy_name="scipy_local_powell",
            domain=domain,
            problem_features={
                **_blend,
                "descriptor_mix": "mixed",
                "n_continuous_variables": 1,
                "n_integer_variables": 1,
                "n_categorical_variables": 0,
                "log_discrete_configuration_measure": 1.0,
            },
            performance_metrics={
                "final_value": 0.08,
                "iterations": 40,
                "time": 0.05,
                "success": True,
            },
        )

    selector = StrategySelector(memory=memory)
    features = extract_problem_features(bounds=[(0.0, 1.0)], max_evaluations=500)
    hybrid_excluded = frozenset({"discrete_random_neighborhood", "hybrid_outer_random_inner_scipy"})

    strat_mix, conf_mix, basis_mix = selector.select_with_basis(
        features=features,
        domain=domain,
        exclude_strategies=hybrid_excluded,
        memory_descriptor_mix="mixed",
    )
    assert strat_mix == "scipy_local_powell"
    assert conf_mix >= 0.9
    assert basis_mix == "memory_override"

    strat_plain, _conf_plain, basis_plain = selector.select_with_basis(
        features=features,
        domain=domain,
        exclude_strategies=hybrid_excluded,
    )
    assert strat_plain == "scipy_de"
    assert basis_plain == "memory_override"
