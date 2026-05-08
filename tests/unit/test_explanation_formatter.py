from sematryx_engine import format_explanation_concise, format_explanation_verbose
from sematryx_engine.api.models import OptimizationResult


def _result() -> OptimizationResult:
    return OptimizationResult(
        best_solution=[0.0, 0.0],
        best_value=0.01,
        evaluations=42,
        strategy_used="scipy_de",
        success=True,
        explanation={
            "selection_basis": "bandit",
            "selection_confidence": 0.81,
            "strategy_used": "scipy_de",
            "topology_tunneling_directive": "balanced",
            "topology_physarum_tunneling_score": 0.63,
            "tuning_priors": {"version": 1},
            "adaptation": {
                "topology_budget_regime": "generous",
                "problem_complexity": "medium",
                "global_evaluation_budget": 500,
                "winning_attempt": 1,
            },
            "attempts": [
                {
                    "attempt": 1,
                    "strategy": "scipy_de",
                    "best_value": 0.01,
                    "budget_allocated": 200,
                    "success": True,
                }
            ],
        },
    )


def test_concise_formatter_output_contains_core_fields() -> None:
    text = format_explanation_concise(_result())
    assert "strategy=scipy_de" in text
    assert "basis=bandit" in text
    assert "attempts=1" in text


def test_verbose_formatter_output_contains_adaptation_and_attempts() -> None:
    text = format_explanation_verbose(_result())
    assert "Explanation" in text
    assert "Adaptation:" in text
    assert "Attempts:" in text
