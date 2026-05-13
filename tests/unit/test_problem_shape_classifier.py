from sematryx_engine.engine.problem_shape_classifier import build_problem_shape


def test_build_problem_shape_schema() -> None:
    artifact = build_problem_shape(
        bounds=[(-5.0, 5.0), (-2.0, 2.0), (0.0, 1.0)],
        max_evaluations=150,
    )
    payload = artifact.as_dict()

    assert payload["version"] == 2
    assert payload["dimensions"] == 3
    assert payload["min_span"] == 1.0
    assert payload["max_span"] == 10.0
    assert payload["avg_span"] == 5.0
    assert payload["budget_regime"] == "moderate"
    assert payload["complexity_hint"] == "medium"
    assert isinstance(payload["shape_routing_score"], float)
    assert payload["shape_routing_directive"] in {"local", "balanced", "aggressive"}
