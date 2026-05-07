from collections.abc import Callable

from sematryx_engine.api.models import OptimizationResult
from sematryx_engine.engine.optimizer import run_optimization


def optimize(
    objective_function: Callable[[list[float]], float],
    bounds: list[tuple[float, float]],
    max_evaluations: int = 1000,
    domain: str = "general",
) -> OptimizationResult:
    return run_optimization(
        objective_function=objective_function,
        bounds=bounds,
        max_evaluations=max_evaluations,
        domain=domain,
    )
