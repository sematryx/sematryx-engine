"""Mixed discrete + continuous optimization via outer random discrete search and inner SciPy."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence

from scipy.optimize import OptimizeResult

from sematryx_engine.api.variable_descriptors import (
    VariableDescriptor,
    normalize_mixed_solution,
)
from sematryx_engine.solvers.discrete_solvers import (
    normalize_discrete_solution,
    sample_random_assignment,
)
from sematryx_engine.solvers.strategy_dispatch import solve_with_strategy


def merge_mixed_solution(
    descriptors: list[VariableDescriptor],
    continuous_values: Sequence[float],
    discrete_values: Sequence[float],
) -> list[float]:
    ci = iter(continuous_values)
    di = iter(discrete_values)
    out: list[float] = []
    for desc in descriptors:
        if desc.kind == "continuous":
            out.append(float(next(ci)))
        else:
            out.append(float(next(di)))
    return out


def continuous_bounds_only(descriptors: list[VariableDescriptor]) -> list[tuple[float, float]]:
    bounds: list[tuple[float, float]] = []
    for desc in descriptors:
        if desc.kind == "continuous":
            assert desc.low is not None and desc.high is not None
            bounds.append((desc.low, desc.high))
    return bounds


def discrete_descriptors_only(descriptors: list[VariableDescriptor]) -> list[VariableDescriptor]:
    return [d for d in descriptors if d.kind != "continuous"]


def solve_hybrid_outer_random_inner_scipy(
    objective_function: Callable[[list[float]], float],
    descriptors: list[VariableDescriptor],
    max_evaluations: int,
    *,
    inner_strategy: str,
    tuning_priors: dict[str, object] | None,
    rng: random.Random | None = None,
) -> OptimizeResult:
    """Sample discrete assignments; for each, optimize continuous coordinates with SciPy."""
    if max_evaluations < 2:
        raise ValueError("hybrid solver requires max_evaluations >= 2.")
    disc_desc = discrete_descriptors_only(descriptors)
    cont_bounds = continuous_bounds_only(descriptors)
    if not disc_desc:
        raise ValueError("hybrid solver requires at least one discrete variable.")
    if not cont_bounds:
        raise ValueError("hybrid solver requires at least one continuous variable.")

    local_rng = rng if rng is not None else random.Random()
    total_nfev = 0
    best_fun = math.inf
    best_x: list[float] | None = None

    outer_cap = max(2, min(40, max(1, max_evaluations // 30)))

    for k in range(outer_cap):
        if total_nfev >= max_evaluations:
            break
        remaining = max_evaluations - total_nfev
        if remaining < 2:
            break

        disc_sample = sample_random_assignment(disc_desc, local_rng)
        disc_norm = normalize_discrete_solution(disc_sample, disc_desc)

        inner_budget = max(15, remaining // max(1, outer_cap - k))
        inner_budget = min(inner_budget, remaining)

        def wrapped(x_cont: list[float]) -> float:
            full = merge_mixed_solution(descriptors, x_cont, disc_norm)
            full_n = normalize_mixed_solution(full, descriptors)
            return objective_function(full_n)

        scipy_result = solve_with_strategy(
            strategy=inner_strategy,
            objective_function=wrapped,
            bounds=cont_bounds,
            max_evaluations=inner_budget,
            tuning_priors=tuning_priors,
        )
        total_nfev += int(getattr(scipy_result, "nfev", 0))
        val = float(scipy_result.fun)
        merged = merge_mixed_solution(descriptors, list(scipy_result.x), disc_norm)
        merged_n = normalize_mixed_solution(merged, descriptors)
        if val < best_fun:
            best_fun = val
            best_x = merged_n

    assert best_x is not None
    return OptimizeResult(
        x=list(best_x),
        fun=float(best_fun),
        nfev=total_nfev,
        nit=outer_cap,
        success=math.isfinite(best_fun),
        message="hybrid_outer_random_inner_scipy",
    )
