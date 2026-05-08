from __future__ import annotations

from sematryx_engine.api.models import OptimizationResult


def format_explanation_concise(result: OptimizationResult) -> str:
    if result.explanation is None:
        return "No explanation metadata available."

    basis = str(result.explanation.get("selection_basis", "unknown"))
    strategy = str(result.explanation.get("strategy_used", result.strategy_used))
    confidence = result.explanation.get("selection_confidence", 0.0)
    confidence_value = float(confidence) if isinstance(confidence, (int, float)) else 0.0
    attempts = result.explanation.get("attempts", [])
    attempt_count = len(attempts) if isinstance(attempts, list) else 0

    return (
        f"strategy={strategy}; basis={basis}; confidence={confidence_value:.3f}; "
        f"attempts={attempt_count}; best_value={result.best_value:.6g}"
    )


def format_explanation_verbose(result: OptimizationResult) -> str:
    if result.explanation is None:
        return "No explanation metadata available."

    lines = [
        "Explanation",
        f"- Strategy used: {result.explanation.get('strategy_used', result.strategy_used)}",
        f"- Selection basis: {result.explanation.get('selection_basis', 'unknown')}",
        f"- Selection confidence: {result.explanation.get('selection_confidence', 'n/a')}",
        f"- Topology tunneling directive: {result.explanation.get('topology_tunneling_directive', 'n/a')}",
        f"- Topology Physarum score: {result.explanation.get('topology_physarum_tunneling_score', 'n/a')}",
    ]

    tuning = result.explanation.get("tuning_priors")
    if isinstance(tuning, dict):
        lines.append(f"- Tuning priors: {tuning}")

    adaptation = result.explanation.get("adaptation")
    if isinstance(adaptation, dict):
        lines.append("- Adaptation:")
        for key in [
            "topology_budget_regime",
            "problem_complexity",
            "global_evaluation_budget",
            "winning_attempt",
        ]:
            if key in adaptation:
                lines.append(f"  - {key}: {adaptation[key]}")

    attempts = result.explanation.get("attempts")
    if isinstance(attempts, list) and attempts:
        lines.append("- Attempts:")
        for row in attempts:
            if not isinstance(row, dict):
                continue
            lines.append(
                "  - "
                + ", ".join(
                    [
                        f"attempt={row.get('attempt')}",
                        f"strategy={row.get('strategy')}",
                        f"value={row.get('best_value')}",
                        f"budget={row.get('budget_allocated')}",
                        f"success={row.get('success')}",
                    ]
                )
            )

    return "\n".join(lines)
