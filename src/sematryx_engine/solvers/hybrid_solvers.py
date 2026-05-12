"""Mixed discrete + continuous optimization via outer discrete search and inner SciPy."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from scipy.optimize import OptimizeResult

from sematryx_engine.api.variable_descriptors import (
    VariableDescriptor,
    normalize_mixed_solution,
)
from sematryx_engine.engine.ablation import AblationConfig, coerce
from sematryx_engine.solvers.discrete_solvers import (
    discrete_coordinate_neighbors,
    normalize_discrete_solution,
    sample_random_assignment,
)
from sematryx_engine.solvers.strategy_dispatch import solve_with_strategy


@dataclass(slots=True)
class _ShellStat:
    best_y: float
    visits: int


def _lcb_acquire_score(
    key: tuple[float, ...],
    shell_stats: dict[tuple[float, ...], _ShellStat],
    outer_t: int,
    global_best: float,
    *,
    k: float = 0.45,
    optimism: float = 0.85,
) -> float:
    """Lower is better (minimize objective). Unvisited shells are optimistic."""
    if key not in shell_stats:
        anchor = global_best if math.isfinite(global_best) else 0.0
        return anchor - optimism
    st = shell_stats[key]
    bonus = k * math.sqrt(math.log(max(outer_t, 1) + 1) / (st.visits + 0.5))
    return st.best_y - bonus


def _record_shell(
    shell_stats: dict[tuple[float, ...], _ShellStat],
    key: tuple[float, ...],
    y: float,
) -> None:
    if key in shell_stats:
        st = shell_stats[key]
        shell_stats[key] = _ShellStat(min(st.best_y, y), st.visits + 1)
    else:
        shell_stats[key] = _ShellStat(y, 1)


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


def _inner_budget_explore(remaining: int, idx: int, outer_cap: int) -> int:
    """Staged budget: early wider spread, later concentrates via sqrt-shaped split."""
    denom = max(1, outer_cap - idx)
    base = max(15, remaining // denom)
    cap = max(15, int(remaining ** 0.5 * 3))
    return min(remaining, min(base, cap))


def _inner_budget_refine(remaining: int) -> int:
    return max(15, min(remaining, max(28, remaining // 3)))


def solve_hybrid_outer_random_inner_scipy(
    objective_function: Callable[[list[float]], float],
    descriptors: list[VariableDescriptor],
    max_evaluations: int,
    *,
    inner_strategy: str,
    tuning_priors: dict[str, object] | None,
    rng: random.Random | None = None,
    ablation: AblationConfig | None = None,
) -> OptimizeResult:
    """Outer discrete search with LCB-style acquisition + inner SciPy per shell.

    Random proposals and neighbors of the incumbent form a candidate pool each exploration
    step; the shell with lowest lower-confidence-bound score is evaluated next. Refinement
    visits unseen neighbors sorted by the same acquisition scores.
    """
    if max_evaluations < 2:
        raise ValueError("hybrid solver requires max_evaluations >= 2.")
    ab = coerce(ablation)
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
    shell_stats: dict[tuple[float, ...], _ShellStat] = {}
    outer_t = 0
    outer_iterations = 0

    outer_explore_cap = max(2, min(40, max(1, max_evaluations // 30)))

    def run_inner(disc_norm: list[float], inner_budget: int) -> float:
        nonlocal total_nfev, best_fun, best_x, best_disc_norm, outer_iterations, outer_t

        key = tuple(disc_norm)
        seen_disc.add(key)
        outer_iterations += 1

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
        outer_t += 1
        _record_shell(shell_stats, key, val)
        merged = merge_mixed_solution(descriptors, list(scipy_result.x), disc_norm)
        merged_n = normalize_mixed_solution(merged, descriptors)
        if val < best_fun:
            best_fun = val
            best_x = merged_n
            best_disc_norm = list(disc_norm)
        return val

    for idx in range(outer_explore_cap):
        if total_nfev >= max_evaluations:
            break
        remaining = max_evaluations - total_nfev
        if remaining < 2:
            break

        pool_keys: list[tuple[float, ...]] = []
        for _ in range(10):
            dn = normalize_discrete_solution(sample_random_assignment(disc_desc, local_rng), disc_desc)
            kt = tuple(dn)
            if kt not in seen_disc and kt not in pool_keys:
                pool_keys.append(kt)
        if best_disc_norm is not None:
            for dim in range(len(disc_desc)):
                for nbr in discrete_coordinate_neighbors(best_disc_norm, disc_desc, dim):
                    nn = normalize_discrete_solution(nbr, disc_desc)
                    kt = tuple(nn)
                    if kt not in seen_disc and kt not in pool_keys:
                        pool_keys.append(kt)

        if not pool_keys:
            dn = normalize_discrete_solution(sample_random_assignment(disc_desc, local_rng), disc_desc)
            kt = tuple(dn)
            if kt in seen_disc:
                continue
            pool_keys.append(kt)

        if ab.hybrid_outer_acquisition:
            chosen = min(
                pool_keys,
                key=lambda k: _lcb_acquire_score(k, shell_stats, outer_t, best_fun),
            )
        else:
            chosen = local_rng.choice(pool_keys)
        remaining = max_evaluations - total_nfev
        if remaining < 2:
            break
        inner_budget = _inner_budget_explore(remaining, idx, outer_explore_cap)
        inner_budget = min(inner_budget, remaining)
        run_inner(list(chosen), inner_budget)

    if best_x is None or best_disc_norm is None:
        disc_norm = normalize_discrete_solution(
            sample_random_assignment(disc_desc, local_rng),
            disc_desc,
        )
        remaining = max_evaluations - total_nfev
        if remaining >= 2:
            inner_budget = max(15, min(remaining, max(20, remaining // 4)))
            inner_budget = min(inner_budget, remaining)
            key = tuple(disc_norm)
            if key not in seen_disc:
                run_inner(disc_norm, inner_budget)

    assert best_x is not None and best_disc_norm is not None

    if ab.hybrid_outer_refinement:
        improved = True
        while total_nfev < max_evaluations - 1 and improved:
            improved = False
            nbr_candidates: list[tuple[float, ...]] = []
            for dim in range(len(disc_desc)):
                for nbr in discrete_coordinate_neighbors(best_disc_norm, disc_desc, dim):
                    nn = normalize_discrete_solution(nbr, disc_desc)
                    kt = tuple(nn)
                    if kt not in seen_disc and kt not in nbr_candidates:
                        nbr_candidates.append(kt)

            nbr_candidates.sort(
                key=lambda k: _lcb_acquire_score(k, shell_stats, outer_t, best_fun),
            )

            for chosen in nbr_candidates:
                if total_nfev >= max_evaluations:
                    break
                remaining = max_evaluations - total_nfev
                if remaining < 2:
                    break
                inner_budget = _inner_budget_refine(remaining)
                inner_budget = min(inner_budget, remaining)
                prev_best = best_fun
                run_inner(list(chosen), inner_budget)
                if best_fun < prev_best - 1e-15:
                    improved = True
                    break

    assert best_x is not None
    if ab.is_default():
        message = "hybrid_outer_acquisition_lcb_inner_scipy_refined"
    else:
        acq = "lcb" if ab.hybrid_outer_acquisition else "uniform"
        ref = "refined" if ab.hybrid_outer_refinement else "no_refine"
        message = f"hybrid_outer_{acq}_inner_scipy_{ref}"
    return OptimizeResult(
        x=list(best_x),
        fun=float(best_fun),
        nfev=total_nfev,
        nit=outer_iterations,
        success=math.isfinite(best_fun),
        message=message,
    )
