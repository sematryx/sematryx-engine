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
