"""Toy discrete validation scenarios (knapsack- and assignment-shaped) for Stage 3 benchmarks."""

from __future__ import annotations

from collections.abc import Callable


def knapsack_01_penalty_objective(
    weights: list[int],
    values: list[int],
    capacity: int,
) -> Callable[[list[float]], float]:
    """0/1 knapsack as minimization: feasible configs minimize negative total value."""

    n = len(weights)

    def objective(x: list[float]) -> float:
        picks = [max(0, min(1, int(round(x[i])))) for i in range(n)]
        weight_sum = sum(weights[i] * picks[i] for i in range(n))
        value_sum = sum(values[i] * picks[i] for i in range(n))
        if weight_sum > capacity:
            return 1e6 + float(weight_sum - capacity)
        return float(-value_sum)

    return objective


def knapsack_01_small_specs() -> tuple[list[int], list[int], int, float]:
    """Four items; optimum profit 10 (pick items at indices 1 and 3, weight 8)."""
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 8
    optimal_profit = 10.0
    return weights, values, capacity, optimal_profit


def knapsack_01_variable_descriptors() -> list[dict[str, object]]:
    return [{"kind": "integer", "low": 0, "high": 1} for _ in range(4)]


def assignment_2x2_penalty_objective(
    cost: list[list[int]],
) -> Callable[[list[float]], float]:
    """Two workers choose distinct tasks (indices 0..1); duplicate assignment incurs large penalty."""

    def objective(x: list[float]) -> float:
        a0 = max(0, min(1, int(round(x[0]))))
        a1 = max(0, min(1, int(round(x[1]))))
        if a0 == a1:
            return 100.0
        return float(cost[0][a0] + cost[1][a1])

    return objective


def assignment_2x2_specs() -> tuple[list[list[int]], float]:
    """Optimal disjoint assignment cost = 1 + 2 = 3."""
    cost = [[1, 4], [3, 2]]
    optimal_cost = 3.0
    return cost, optimal_cost


def assignment_2x2_variable_descriptors() -> list[dict[str, object]]:
    return [
        {"kind": "categorical", "categories": ["t0", "t1"]},
        {"kind": "categorical", "categories": ["t0", "t1"]},
    ]
