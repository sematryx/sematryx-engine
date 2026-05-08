from sematryx_engine.api.models import OptimizationResult


def test_result_model_fields() -> None:
    result = OptimizationResult(
        best_solution=[0.0, 0.0],
        best_value=0.0,
        evaluations=1,
        strategy_used="test",
        success=True,
    )
    assert result.strategy_used == "test"


def test_result_model_topology_optional_field() -> None:
    plain = OptimizationResult(
        best_solution=[0.0],
        best_value=1.0,
        evaluations=2,
        strategy_used="plain",
        success=True,
    )
    with_topology = OptimizationResult(
        best_solution=[0.0],
        best_value=1.0,
        evaluations=2,
        strategy_used="plain",
        success=True,
        topology_artifact={"version": 1, "dimensions": 1},
    )
    assert plain.topology_artifact is None
    assert with_topology.topology_artifact is not None


def test_result_model_explanation_optional_field() -> None:
    result = OptimizationResult(
        best_solution=[0.0],
        best_value=1.0,
        evaluations=2,
        strategy_used="plain",
        success=True,
        explanation={"selection_basis": "bandit"},
    )
    assert result.explanation is not None
    assert result.explanation["selection_basis"] == "bandit"
