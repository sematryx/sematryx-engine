from sematryx_engine.engine.problem_features import extract_problem_features


def test_extract_problem_features_low_complexity() -> None:
    features = extract_problem_features(
        bounds=[(-1.0, 1.0), (-2.0, 2.0)],
        max_evaluations=500,
    )
    assert features.dimensions == 2
    assert features.bounded is True
    assert features.complexity == "low"
