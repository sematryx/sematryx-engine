from dataclasses import dataclass


@dataclass(slots=True)
class OptimizationResult:
    best_solution: list[float]
    best_value: float
    evaluations: int
    strategy_used: str
    success: bool
    topology_artifact: dict[str, object] | None = None
    explanation: dict[str, object] | None = None
