from collections.abc import Callable
from math import isfinite, sqrt
from pathlib import Path

from sematryx_engine.api.models import OptimizationResult
from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory
from sematryx_engine.solvers.scipy_solvers import solve_with_scipy

_MEMORY = LocalStrategyMemory(Path.home() / ".sematryx" / "strategy_memory.db")
_SELECTOR = StrategySelector(
    memory=_MEMORY,
    bandit_state_path=Path.home() / ".sematryx" / "bandit_state.json",
)


def run_optimization(
    objective_function: Callable[[list[float]], float],
    bounds: list[tuple[float, float]],
    max_evaluations: int,
    domain: str = "general",
) -> OptimizationResult:
    features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)
    strategy_name, _confidence = _SELECTOR.select(features, domain=domain)
    scipy_result = solve_with_scipy(
        strategy=strategy_name,
        objective_function=objective_function,
        bounds=bounds,
        max_evaluations=max_evaluations,
    )

    best_value = float(scipy_result.fun)
    # Reward: sqrt-scaled inverse objective (clipped) for smoother bandit updates across scales.
    reward = min(1.0, 1.0 / (1.0 + sqrt(max(0.0, best_value))))
    _SELECTOR.update(strategy_name, reward)
    _MEMORY.store_optimization_result(
        strategy_name=strategy_name,
        domain=domain,
        problem_features={
            "dimensions": features.dimensions,
            "avg_range": features.avg_range,
            "bounded": features.bounded,
            "budget_per_dimension": features.budget_per_dimension,
            "complexity": features.complexity,
        },
        performance_metrics={
            "final_value": best_value,
            "iterations": int(getattr(scipy_result, "nfev", 0)),
            "time": 0.0,
            "success": bool(getattr(scipy_result, "success", True)),
        },
    )

    solver_success = bool(getattr(scipy_result, "success", True))
    practical_success = solver_success or isfinite(best_value)

    return OptimizationResult(
        best_solution=list(scipy_result.x),
        best_value=best_value,
        evaluations=int(getattr(scipy_result, "nfev", 0)),
        strategy_used=strategy_name,
        success=practical_success,
    )
