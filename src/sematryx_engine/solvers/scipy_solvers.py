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
    tuning_priors: dict[str, object] | None = None,
) -> OptimizeResult:
    dims = max(len(bounds), 1)

    if strategy == "scipy_de":
        maxiter = max(1, max_evaluations // dims)
        polish = True
        popsize = 15
        if tuning_priors is not None:
            if tuning_priors.get("de_polish") is False:
                polish = False
            raw_pop = tuning_priors.get("de_population_scale", 1.0)
            pop_scale = float(raw_pop) if isinstance(raw_pop, (int, float)) else 1.0
            popsize = max(5, min(35, int(round(15.0 * pop_scale))))
        return differential_evolution(
            func=objective_function,
            bounds=bounds,
            maxiter=maxiter,
            polish=polish,
            popsize=popsize,
            seed=42,
        )

    if strategy == "scipy_dual_annealing":
        if tuning_priors is not None:
            raw_rtr = tuning_priors.get("dual_annealing_restart_temp_ratio")
            if isinstance(raw_rtr, (int, float)) and float(raw_rtr) > 0.0:
                return dual_annealing(
                    func=objective_function,
                    bounds=bounds,
                    maxfun=max_evaluations,
                    seed=42,
                    restart_temp_ratio=float(raw_rtr),
                )
        return dual_annealing(
            func=objective_function,
            bounds=bounds,
            maxfun=max_evaluations,
            seed=42,
        )

    if strategy == "scipy_shgo":
        base_n = max(20, min(80, max_evaluations // dims))
        n = base_n
        if tuning_priors is not None:
            raw_scale = tuning_priors.get("shgo_sampling_scale", 1.0)
            scale = float(raw_scale) if isinstance(raw_scale, (int, float)) else 1.0
            n = max(15, min(100, int(round(float(base_n) * scale))))
        return shgo(
            func=objective_function,
            bounds=bounds,
            n=n,
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
