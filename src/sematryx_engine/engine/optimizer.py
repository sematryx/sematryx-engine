from collections.abc import Callable
from math import isfinite, sqrt
from pathlib import Path

from sematryx_engine.api.models import OptimizationResult
from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.engine.topology import build_topology_artifact
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory
from sematryx_engine.solvers.scipy_solvers import solve_with_scipy

_MEMORY = LocalStrategyMemory(Path.home() / ".sematryx" / "strategy_memory.db")
_SELECTOR = StrategySelector(
    memory=_MEMORY,
    bandit_state_path=Path.home() / ".sematryx" / "bandit_state.json",
)


def _attempt_budget(
    *,
    max_evaluations: int,
    topology_budget_regime: str,
) -> int:
    if topology_budget_regime == "generous":
        return 3
    if topology_budget_regime == "moderate":
        return 2
    return 1


def _fallback_strategy(primary: str) -> str:
    fallback_map = {
        "scipy_dual_annealing": "scipy_de",
        "scipy_de": "scipy_local_lbfgsb",
        "scipy_local_lbfgsb": "scipy_dual_annealing",
        "scipy_shgo": "scipy_de",
    }
    return fallback_map.get(primary, "scipy_de")


def run_optimization(
    objective_function: Callable[[list[float]], float],
    bounds: list[tuple[float, float]],
    max_evaluations: int,
    domain: str = "general",
) -> OptimizationResult:
    features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)
    topology_artifact = build_topology_artifact(
        bounds=bounds,
        max_evaluations=max_evaluations,
    )
    strategy_name, selection_confidence, selection_basis = _SELECTOR.select_with_basis(
        features=features,
        domain=domain,
        topology_artifact=topology_artifact.as_dict(),
    )
    attempt_limit = _attempt_budget(
        max_evaluations=max_evaluations,
        topology_budget_regime=topology_artifact.budget_regime,
    )
    per_attempt_budget = max(20, max_evaluations // attempt_limit)
    attempt_plan = [strategy_name]
    while len(attempt_plan) < attempt_limit:
        attempt_plan.append(_fallback_strategy(attempt_plan[-1]))

    best_result = None
    best_strategy = strategy_name
    attempt_records: list[dict[str, object]] = []
    for idx, attempt_strategy in enumerate(attempt_plan, start=1):
        scipy_result = solve_with_scipy(
            strategy=attempt_strategy,
            objective_function=objective_function,
            bounds=bounds,
            max_evaluations=per_attempt_budget,
        )
        value = float(scipy_result.fun)
        attempt_records.append(
            {
                "attempt": idx,
                "strategy": attempt_strategy,
                "best_value": value,
                "evaluations": int(getattr(scipy_result, "nfev", 0)),
                "success": bool(getattr(scipy_result, "success", True)),
            }
        )
        if best_result is None or value < float(best_result.fun):
            best_result = scipy_result
            best_strategy = attempt_strategy

    assert best_result is not None
    scipy_result = best_result

    best_value = float(scipy_result.fun)
    # Reward: sqrt-scaled inverse objective (clipped) for smoother bandit updates across scales.
    reward = min(1.0, 1.0 / (1.0 + sqrt(max(0.0, best_value))))
    _SELECTOR.update(best_strategy, reward)
    _MEMORY.store_optimization_result(
        strategy_name=best_strategy,
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
        strategy_used=best_strategy,
        success=practical_success,
        topology_artifact=topology_artifact.as_dict(),
        explanation={
            "selection_basis": selection_basis,
            "selection_confidence": selection_confidence,
            "domain": domain,
            "strategy_used": best_strategy,
            "topology_tunneling_directive": topology_artifact.tunneling_directive,
            "topology_physarum_tunneling_score": topology_artifact.physarum_tunneling_score,
            "attempt_limit": attempt_limit,
            "attempts": attempt_records,
        },
    )
