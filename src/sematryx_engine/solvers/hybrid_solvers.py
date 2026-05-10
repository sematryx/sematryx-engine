"""Mixed discrete + continuous optimization via outer discrete search and inner SciPy."""

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
    discrete_coordinate_neighbors,
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
    """Sample discrete assignments; for each, optimize continuous coordinates with SciPy.

    Outer loop: uniform random exploration, then coordinate neighborhood refinement around the
    best discrete shell found (hill-climbing in discrete space with inner continuous solves).
    """
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
    best_disc_norm: list[float] | None = None
    seen_disc: set[tuple[float, ...]] = set()
    outer_iterations = 0

    def inner_budget_refine(remaining: int) -> int:
        return max(15, min(remaining, max(25, remaining // 3)))

    outer_explore_cap = max(2, min(40, max(1, max_evaluations // 30)))

    for k in range(outer_explore_cap):
        if total_nfev >= max_evaluations:
            break
        remaining = max_evaluations - total_nfev
        if remaining < 2:
            break

        disc_sample = sample_random_assignment(disc_desc, local_rng)
        disc_norm = normalize_discrete_solution(disc_sample, disc_desc)
        key = tuple(disc_norm)
        if key in seen_disc:
            continue

        remaining = max_evaluations - total_nfev
        if remaining < 2:
            break
        inner_budget = max(15, remaining // max(1, outer_explore_cap - k))
        inner_budget = min(inner_budget, remaining)

        seen_disc.add(key)
        outer_iterations += 1

        def wrapped_explore(x_cont: list[float]) -> float:
            full = merge_mixed_solution(descriptors, x_cont, disc_norm)
            full_n = normalize_mixed_solution(full, descriptors)
            return objective_function(full_n)

        scipy_result = solve_with_strategy(
            strategy=inner_strategy,
            objective_function=wrapped_explore,
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
            best_disc_norm = list(disc_norm)

    if best_x is None or best_disc_norm is None:
        disc_norm = normalize_discrete_solution(
            sample_random_assignment(disc_desc, local_rng),
            disc_desc,
        )
        remaining = max_evaluations - total_nfev
        if remaining >= 2:
            inner_budget = max(15, min(remaining, max(20, remaining // 4)))
            inner_budget = min(inner_budget, remaining)
            outer_iterations += 1

            def wrapped_fallback(x_cont: list[float]) -> float:
                full = merge_mixed_solution(descriptors, x_cont, disc_norm)
                full_n = normalize_mixed_solution(full, descriptors)
                return objective_function(full_n)

            scipy_result = solve_with_strategy(
                strategy=inner_strategy,
                objective_function=wrapped_fallback,
                bounds=cont_bounds,
                max_evaluations=inner_budget,
                tuning_priors=tuning_priors,
            )
            total_nfev += int(getattr(scipy_result, "nfev", 0))
            val = float(scipy_result.fun)
            merged = merge_mixed_solution(descriptors, list(scipy_result.x), disc_norm)
            merged_n = normalize_mixed_solution(merged, descriptors)
            best_fun = val
            best_x = merged_n
            best_disc_norm = list(disc_norm)
            seen_disc.add(tuple(disc_norm))

    assert best_x is not None and best_disc_norm is not None

    improved = True
    dim_order = list(range(len(disc_desc)))
    while total_nfev < max_evaluations - 1 and improved:
        improved = False
        local_rng.shuffle(dim_order)
        for dim in dim_order:
            if total_nfev >= max_evaluations:
                break
            for nbr in discrete_coordinate_neighbors(best_disc_norm, disc_desc, dim):
                remaining = max_evaluations - total_nfev
                if remaining < 2:
                    break
                nbr_norm = normalize_discrete_solution(nbr, disc_desc)
                key = tuple(nbr_norm)
                if key in seen_disc:
                    continue
                seen_disc.add(key)
                remaining = max_evaluations - total_nfev
                inner_budget = inner_budget_refine(remaining)
                inner_budget = min(inner_budget, remaining)

                def wrapped_refine(x_cont: list[float]) -> float:
                    full = merge_mixed_solution(descriptors, x_cont, nbr_norm)
                    full_n = normalize_mixed_solution(full, descriptors)
                    return objective_function(full_n)

                outer_iterations += 1
                scipy_result = solve_with_strategy(
                    strategy=inner_strategy,
                    objective_function=wrapped_refine,
                    bounds=cont_bounds,
                    max_evaluations=inner_budget,
                    tuning_priors=tuning_priors,
                )
                total_nfev += int(getattr(scipy_result, "nfev", 0))
                val = float(scipy_result.fun)
                merged = merge_mixed_solution(descriptors, list(scipy_result.x), nbr_norm)
                merged_n = normalize_mixed_solution(merged, descriptors)
                if val < best_fun:
                    best_fun = val
                    best_x = merged_n
                    best_disc_norm = list(nbr_norm)
                    improved = True
                    break
            if improved:
                break

    assert best_x is not None
    return OptimizeResult(
        x=list(best_x),
        fun=float(best_fun),
        nfev=total_nfev,
        nit=outer_iterations,
        success=math.isfinite(best_fun),
        message="hybrid_outer_random_inner_scipy_refined",
    )
