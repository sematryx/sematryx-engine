from collections.abc import Callable

from scipy.optimize import (
    Bounds,
    OptimizeResult,
    differential_evolution,
    dual_annealing,
    minimize,
    shgo,
)


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

    if strategy == "scipy_shgo":
        return shgo(
            func=objective_function,
            bounds=bounds,
            n=max(20, min(80, max_evaluations // max(len(bounds), 1))),
        )

    lows, highs = _to_sequence_bounds(bounds)
    x0 = [(low + high) / 2.0 for low, high in zip(lows, highs, strict=True)]
    local_method_map = {
        "scipy_local_lbfgsb": "L-BFGS-B",
        "scipy_local_powell": "Powell",
        "scipy_local_tnc": "TNC",
        "scipy_local_slsqp": "SLSQP",
        "scipy_local_cobyla": "COBYLA",
        "scipy_local_nelder_mead": "Nelder-Mead",
        "scipy_local_cg": "CG",
    }
    method = local_method_map.get(strategy)
    if method is None:
        raise ValueError(f"Unsupported scipy strategy: {strategy}")

    maxiter = max(20, max_evaluations // max(len(bounds), 1))
    if method == "L-BFGS-B":
        options: dict[str, int] = {"maxiter": maxiter, "maxfun": max_evaluations}
    elif method == "TNC":
        options = {"maxfun": max_evaluations}
    else:
        options = {"maxiter": maxiter}

    bounds_arg: Bounds | None = Bounds(lows, highs)
    if method in {"Nelder-Mead", "CG"}:
        bounds_arg = None

    return minimize(
        fun=objective_function,
        x0=x0,
        method=method,
        bounds=bounds_arg,
        options=options,
    )
