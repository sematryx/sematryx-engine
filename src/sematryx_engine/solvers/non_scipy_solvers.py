from __future__ import annotations

from collections.abc import Callable

from scipy.optimize import OptimizeResult


def available_optional_strategies() -> list[str]:
    import importlib.util

    out: list[str] = []
    if importlib.util.find_spec("cma") is not None:
        out.append("cma_es")
    if importlib.util.find_spec("skopt") is not None:
        out.extend(["skopt_gp", "skopt_forest", "skopt_gbrt"])
    return out


def _result_from_point(x: list[float], value: float, success: bool) -> OptimizeResult:
    return OptimizeResult(x=x, fun=value, success=success, nfev=0)


def solve_with_non_scipy(
    *,
    strategy: str,
    objective_function: Callable[[list[float]], float],
    bounds: list[tuple[float, float]],
    max_evaluations: int,
) -> OptimizeResult:
    if strategy == "cma_es":
        import cma

        x0 = [(low + high) / 2.0 for low, high in bounds]
        sigma0 = max((high - low) for low, high in bounds) / 6.0
        opts = {"bounds": [[low for low, _ in bounds], [high for _, high in bounds]], "maxfevals": max_evaluations, "seed": 42, "verbose": -9}
        xbest, fbest, _, _, _, _ = cma.fmin2(objective_function, x0, sigma0, options=opts)
        return _result_from_point(list(xbest), float(fbest), True)

    if strategy in {"skopt_gp", "skopt_forest", "skopt_gbrt"}:
        from skopt import forest_minimize, gbrt_minimize, gp_minimize
        from skopt.space import Real

        dims = [Real(low, high) for low, high in bounds]
        mapper = {
            "skopt_gp": gp_minimize,
            "skopt_forest": forest_minimize,
            "skopt_gbrt": gbrt_minimize,
        }
        fn = mapper[strategy]
        result = fn(objective_function, dims, n_calls=max(20, max_evaluations // 2), random_state=42)
        return _result_from_point(list(result.x), float(result.fun), True)

    raise ValueError(f"Unsupported non-scipy strategy: {strategy}")
