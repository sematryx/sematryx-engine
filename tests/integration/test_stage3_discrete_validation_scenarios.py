"""Stage 3 discrete validation: knapsack- and assignment-shaped toy scenarios."""

from sematryx_engine import optimize
from sematryx_engine.engine.discrete_benchmark_scenarios import (
    assignment_2x2_penalty_objective,
    assignment_2x2_specs,
    assignment_2x2_variable_descriptors,
    knapsack_01_penalty_objective,
    knapsack_01_small_specs,
    knapsack_01_variable_descriptors,
)


def test_discrete_validation_knapsack_01_reaches_known_optimum() -> None:
    weights, values, capacity, optimal_profit = knapsack_01_small_specs()
    objective = knapsack_01_penalty_objective(weights, values, capacity)
    result = optimize(
        objective_function=objective,
        variable_descriptors=knapsack_01_variable_descriptors(),
        max_evaluations=1800,
        domain="stage3_validation_knapsack01",
        rng_seed=20260111,
    )
    assert result.success is True
    assert result.strategy_used == "discrete_random_neighborhood"
    assert result.best_value <= -optimal_profit + 1e-6


def test_discrete_validation_assignment_2x2_reaches_known_optimum() -> None:
    cost, optimal_cost = assignment_2x2_specs()
    objective = assignment_2x2_penalty_objective(cost)
    result = optimize(
        objective_function=objective,
        variable_descriptors=assignment_2x2_variable_descriptors(),
        max_evaluations=900,
        domain="stage3_validation_assignment2x2",
        rng_seed=20260112,
    )
    assert result.success is True
    assert result.strategy_used == "discrete_random_neighborhood"
    assert result.best_value <= optimal_cost + 1e-6
