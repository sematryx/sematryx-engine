from sematryx_engine import (
    format_explanation_concise,
    format_explanation_verbose,
    optimize,
)


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_formatter_helpers_render_runtime_explanation() -> None:
    result = optimize(
        objective_function=sphere,
        bounds=[(-3.0, 3.0)] * 3,
        max_evaluations=500,
        domain="formatter_integration",
    )
    concise = format_explanation_concise(result)
    verbose = format_explanation_verbose(result)

    assert "strategy=" in concise
    assert "basis=" in concise
    assert "attempts=" in concise

    assert "Explanation" in verbose
    assert "Selection basis" in verbose
    assert "Attempts:" in verbose
