from dataclasses import dataclass


@dataclass(slots=True)
class ProblemFeatures:
    dimensions: int
    avg_range: float
    bounded: bool
    budget_per_dimension: float
    complexity: str


def extract_problem_features(
    bounds: list[tuple[float, float]],
    max_evaluations: int,
) -> ProblemFeatures:
    dimensions = len(bounds)
    ranges = [high - low for low, high in bounds]
    avg_range = sum(ranges) / dimensions if dimensions else 0.0
    bounded = all(low < high for low, high in bounds)
    budget_per_dimension = max_evaluations / max(dimensions, 1)

    if dimensions <= 3 and budget_per_dimension >= 100:
        complexity = "low"
    elif dimensions <= 10 and budget_per_dimension >= 30:
        complexity = "medium"
    else:
        complexity = "high"

    return ProblemFeatures(
        dimensions=dimensions,
        avg_range=avg_range,
        bounded=bounded,
        budget_per_dimension=budget_per_dimension,
        complexity=complexity,
    )
