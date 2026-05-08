from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TopologyArtifact:
    version: int
    dimensions: int
    min_span: float
    max_span: float
    avg_span: float
    budget_regime: str
    complexity_hint: str

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "dimensions": self.dimensions,
            "min_span": self.min_span,
            "max_span": self.max_span,
            "avg_span": self.avg_span,
            "budget_regime": self.budget_regime,
            "complexity_hint": self.complexity_hint,
        }


def build_topology_artifact(
    *,
    bounds: list[tuple[float, float]],
    max_evaluations: int,
) -> TopologyArtifact:
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

    return TopologyArtifact(
        version=1,
        dimensions=dimensions,
        min_span=min_span,
        max_span=max_span,
        avg_span=avg_span,
        budget_regime=budget_regime,
        complexity_hint=complexity_hint,
    )
