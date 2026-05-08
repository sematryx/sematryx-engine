from sematryx_engine.engine.topology import build_topology_artifact


def test_build_topology_artifact_schema() -> None:
    artifact = build_topology_artifact(
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
    assert isinstance(payload["physarum_tunneling_score"], float)
    assert payload["tunneling_directive"] in {"local", "balanced", "aggressive"}
