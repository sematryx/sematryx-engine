from __future__ import annotations

from collections.abc import Callable

from scipy.optimize import OptimizeResult

from sematryx_engine.solvers.non_scipy_solvers import solve_with_non_scipy
from sematryx_engine.solvers.scipy_solvers import solve_with_scipy


def solve_with_strategy(
    *,
    strategy: str,
    objective_function: Callable[[list[float]], float],
    bounds: list[tuple[float, float]],
    max_evaluations: int,
    tuning_priors: dict[str, object] | None = None,
) -> OptimizeResult:
    if strategy.startswith("scipy_"):
        return solve_with_scipy(
            strategy=strategy,
            objective_function=objective_function,
            bounds=bounds,
            max_evaluations=max_evaluations,
            tuning_priors=tuning_priors,
        )
    return solve_with_non_scipy(
        strategy=strategy,
        objective_function=objective_function,
        bounds=bounds,
        max_evaluations=max_evaluations,
    )
