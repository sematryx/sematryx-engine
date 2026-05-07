from collections.abc import Callable

from scipy.optimize import Bounds, OptimizeResult, differential_evolution, dual_annealing, minimize


def _to_sequence_bounds(bounds: list[tuple[float, float]]) -> tuple[list[float], list[float]]:
    lows = [low for low, _ in bounds]
    highs = [high for _, high in bounds]
    return lows, highs


def solve_with_scipy(
    strategy: str,
    objective_function: Callable[[list[float]], float],
    bounds: list[tuple[float, float]],
    max_evaluations: int,
) -> OptimizeResult:
    if strategy == "scipy_de":
        return differential_evolution(
            func=objective_function,
            bounds=bounds,
            maxiter=max(1, max_evaluations // max(len(bounds), 1)),
            polish=True,
            seed=42,
        )

    if strategy == "scipy_dual_annealing":
        return dual_annealing(
            func=objective_function,
            bounds=bounds,
            maxfun=max_evaluations,
            seed=42,
        )

    lows, highs = _to_sequence_bounds(bounds)
    x0 = [(low + high) / 2.0 for low, high in zip(lows, highs, strict=True)]
    return minimize(
        fun=objective_function,
        x0=x0,
        method="L-BFGS-B",
        bounds=Bounds(lows, highs),
        options={"maxfun": max_evaluations},
    )
