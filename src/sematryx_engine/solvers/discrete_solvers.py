"""Baseline discrete optimization: random search plus coordinate neighborhood refinement."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence

from scipy.optimize import OptimizeResult

from sematryx_engine.api.variable_descriptors import VariableDescriptor


def _first_valid_assignment(descriptors: list[VariableDescriptor]) -> list[float]:
    vec: list[float] = []
    for desc in descriptors:
        if desc.kind == "integer":
            assert desc.low is not None and desc.high is not None
            lo = math.ceil(float(desc.low))
            hi = math.floor(float(desc.high))
            if lo > hi:
                raise ValueError("integer variable has empty domain after rounding bounds.")
            vec.append(float(lo))
        elif desc.kind == "categorical":
            vec.append(0.0)
        else:
            raise ValueError("_first_valid_assignment expects discrete descriptors only.")
    return vec


def normalize_discrete_solution(
    x: Sequence[float],
    descriptors: list[VariableDescriptor],
) -> list[float]:
    """Map a raw vector to valid encoded values for integer and categorical dimensions."""
    out: list[float] = []
    for xi, desc in zip(x, descriptors, strict=True):
        if desc.kind == "integer":
            assert desc.low is not None and desc.high is not None
            lo = math.ceil(float(desc.low))
            hi = math.floor(float(desc.high))
            v = int(round(float(xi)))
            v = max(lo, min(hi, v))
            out.append(float(v))
        elif desc.kind == "categorical":
            n = len(desc.categories)
            v = int(round(float(xi)))
            v = max(0, min(n - 1, v))
            out.append(float(v))
        else:
            raise ValueError("normalize_discrete_solution expects discrete descriptors only.")
    return out


def sample_random_assignment(
    descriptors: list[VariableDescriptor],
    rng: random.Random,
) -> list[float]:
    vec: list[float] = []
    for desc in descriptors:
        if desc.kind == "integer":
            assert desc.low is not None and desc.high is not None
            lo = math.ceil(float(desc.low))
            hi = math.floor(float(desc.high))
            if lo > hi:
                raise ValueError("integer variable has empty domain after rounding bounds.")
            vec.append(float(rng.randint(lo, hi)))
        elif desc.kind == "categorical":
            vec.append(float(rng.randrange(len(desc.categories))))
        else:
            raise ValueError("sample_random_assignment expects discrete descriptors only.")
    return vec


def _coordinate_neighbors(
    current: list[float],
    descriptors: list[VariableDescriptor],
    dim_index: int,
) -> list[list[float]]:
    """Single-dimension perturbations: ±1 for integers, other categories."""
    desc = descriptors[dim_index]
    neighbors: list[list[float]] = []
    base = list(current)
    if desc.kind == "integer":
        assert desc.low is not None and desc.high is not None
        lo = math.ceil(float(desc.low))
        hi = math.floor(float(desc.high))
        cur = int(round(base[dim_index]))
        for delta in (-1, 1):
            nxt = cur + delta
            if lo <= nxt <= hi:
                cand = list(base)
                cand[dim_index] = float(nxt)
                neighbors.append(cand)
    elif desc.kind == "categorical":
        n = len(desc.categories)
        cur = int(round(base[dim_index]))
        for idx in range(n):
            if idx == cur:
                continue
            cand = list(base)
            cand[dim_index] = float(idx)
            neighbors.append(cand)
    return neighbors


def solve_discrete_baseline(
    objective_function: Callable[[list[float]], float],
    descriptors: list[VariableDescriptor],
    max_evaluations: int,
    *,
    rng: random.Random | None = None,
) -> OptimizeResult:
    """Random search followed by coordinate-descent neighborhood hill climbing."""
    if max_evaluations < 1:
        raise ValueError("max_evaluations must be at least 1.")
    if not descriptors:
        raise ValueError("discrete baseline requires at least one variable.")
    local_rng = rng if rng is not None else random.Random()

    seen: set[tuple[float, ...]] = set()
    nfev = 0

    def eval_new(raw: Sequence[float]) -> tuple[list[float], float] | None:
        nonlocal nfev
        normalized = normalize_discrete_solution(raw, descriptors)
        key = tuple(normalized)
        if key in seen:
            return None
        seen.add(key)
        nfev += 1
        value = float(objective_function(normalized))
        return normalized, value

    random_budget = max(1, (max_evaluations * 2) // 5)
    random_budget = min(random_budget, max_evaluations)

    best_x: list[float] | None = None
    best_fun = math.inf

    for _ in range(random_budget):
        if nfev >= max_evaluations:
            break
        candidate = sample_random_assignment(descriptors, local_rng)
        got = eval_new(candidate)
        if got is None:
            continue
        bx, fv = got
        if fv < best_fun:
            best_fun = fv
            best_x = bx

    if best_x is None:
        fallback = _first_valid_assignment(descriptors)
        best_x = normalize_discrete_solution(fallback, descriptors)
        best_fun = float(objective_function(best_x))
        nfev += 1

    assert best_x is not None

    dim_order = list(range(len(descriptors)))

    while nfev < max_evaluations:
        local_rng.shuffle(dim_order)
        improved = False
        for dim in dim_order:
            if nfev >= max_evaluations:
                break
            for nbr in _coordinate_neighbors(best_x, descriptors, dim):
                if nfev >= max_evaluations:
                    break
                got = eval_new(nbr)
                if got is None:
                    continue
                bx, fv = got
                if fv < best_fun:
                    best_fun = fv
                    best_x = bx
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    return OptimizeResult(
        x=list(best_x),
        fun=float(best_fun),
        nfev=nfev,
        nit=0,
        success=math.isfinite(best_fun),
        message="discrete_random_neighborhood",
    )
