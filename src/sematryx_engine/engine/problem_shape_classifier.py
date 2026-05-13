"""Problem-shape classifier.

Computes a deterministic classification of a problem from its **bounds** and
**evaluation budget** alone — dimension count, bound-width statistics, and
budget-per-dimension. The output drives routing decisions in the strategy selector.

Important: this is **not** topology in the mathematical sense. The function never
samples the objective; it cannot characterise the landscape, basins, ruggedness, or
connectivity. The real topology pipeline (Physarum mapping → topology-informed
tunneling) is a separate slice (see ADR-0026); this classifier is a lightweight
routing prior, not a substitute for landscape analysis.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProblemShape:
    """Deterministic problem-shape classification.

    Carries dimension, bound-width statistics, derived budget regime and
    complexity hint, and a single score + directive used by the selector's
    routing override. None of these signals come from the objective function.
    """

    version: int
    dimensions: int
    min_span: float
    max_span: float
    avg_span: float
    budget_regime: str
    complexity_hint: str
    shape_routing_score: float
    shape_routing_directive: str

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "dimensions": self.dimensions,
            "min_span": self.min_span,
            "max_span": self.max_span,
            "avg_span": self.avg_span,
            "budget_regime": self.budget_regime,
            "complexity_hint": self.complexity_hint,
            "shape_routing_score": self.shape_routing_score,
            "shape_routing_directive": self.shape_routing_directive,
        }


def build_problem_shape(
    *,
    bounds: list[tuple[float, float]],
    max_evaluations: int,
) -> ProblemShape:
    spans = [float(upper - lower) for lower, upper in bounds]
    dimensions = len(spans)
    avg_span = sum(spans) / float(dimensions) if dimensions else 0.0
    min_span = min(spans) if spans else 0.0
    max_span = max(spans) if spans else 0.0
    budget_per_dimension = float(max_evaluations) / float(max(1, dimensions))

    if budget_per_dimension < 50.0:
        budget_regime = "tight"
    elif budget_per_dimension < 200.0:
        budget_regime = "moderate"
    else:
        budget_regime = "generous"

    if dimensions > 12:
        complexity_hint = "high"
    elif avg_span < 3.0:
        complexity_hint = "low"
    else:
        complexity_hint = "medium"

    span_variability = (max_span - min_span) / max(max_span, 1.0)
    if complexity_hint == "high":
        complexity_factor = 1.0
    elif complexity_hint == "medium":
        complexity_factor = 0.7
    else:
        complexity_factor = 0.4

    if budget_regime == "tight":
        budget_factor = 1.0
    elif budget_regime == "moderate":
        budget_factor = 0.7
    else:
        budget_factor = 0.4

    score = min(1.0, max(0.0, 0.45 * complexity_factor + 0.35 * budget_factor + 0.20 * span_variability))
    if score >= 0.75:
        shape_routing_directive = "aggressive"
    elif score >= 0.5:
        shape_routing_directive = "balanced"
    else:
        shape_routing_directive = "local"

    return ProblemShape(
        version=2,
        dimensions=dimensions,
        min_span=min_span,
        max_span=max_span,
        avg_span=avg_span,
        budget_regime=budget_regime,
        complexity_hint=complexity_hint,
        shape_routing_score=round(score, 6),
        shape_routing_directive=shape_routing_directive,
    )
