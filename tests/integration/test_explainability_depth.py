from sematryx_engine import optimize


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_explanation_adaptation_surface_links_topology_retries_and_winner() -> None:
    result = optimize(
        objective_function=sphere,
        bounds=[(-4.0, 4.0)] * 5,
        max_evaluations=800,
        domain="explainability_depth",
    )
    expl = result.explanation
    assert expl is not None
    adaptation = expl["adaptation"]
    assert isinstance(adaptation, dict)

    assert adaptation["topology_budget_regime"] in {"tight", "moderate", "generous"}
    assert adaptation["topology_complexity_hint"] in {"low", "medium", "high"}
    assert adaptation["problem_complexity"] in {"low", "medium", "high"}
    assert isinstance(adaptation["problem_dimensions"], int)
    assert adaptation["problem_dimensions"] == 5
    assert float(adaptation["problem_budget_per_dimension"]) > 0.0
    assert adaptation["global_evaluation_budget"] == 800

    attempt_limit = int(expl["attempt_limit"])
    planned = adaptation["planned_strategies"]
    assert isinstance(planned, list)
    assert len(planned) == attempt_limit

    winner = int(adaptation["winning_attempt"])
    assert 1 <= winner <= attempt_limit
    attempts_by_idx = {int(row["attempt"]): row for row in expl["attempts"]}
    winner_row = attempts_by_idx[winner]
    assert winner_row["strategy"] == result.strategy_used
