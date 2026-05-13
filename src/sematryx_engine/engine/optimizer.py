import random
from collections.abc import Callable
from math import isfinite, sqrt
from pathlib import Path

from sematryx_engine.api.models import OptimizationResult
from sematryx_engine.api.variable_descriptors import (
    VariableDescriptor,
    descriptor_learning_features,
)
from sematryx_engine.engine.ablation import AblationConfig, coerce
from sematryx_engine.engine.problem_features import ProblemFeatures, extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.engine.problem_shape_classifier import build_problem_shape
from sematryx_engine.engine.tuning_priors import compute_solver_tuning_priors, neutral_tuning_priors
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory
from sematryx_engine.solvers.discrete_solvers import solve_discrete_baseline
from sematryx_engine.solvers.hybrid_solvers import (
    continuous_bounds_only,
    solve_hybrid_outer_random_inner_scipy,
)
from sematryx_engine.solvers.strategy_dispatch import solve_with_strategy

_MEMORY = LocalStrategyMemory(Path.home() / ".sematryx" / "strategy_memory.db")
_SELECTOR = StrategySelector(
    memory=_MEMORY,
    bandit_state_path=Path.home() / ".sematryx" / "bandit_state.json",
)


def _attempt_budget(
    *,
    max_evaluations: int,
    budget_regime: str,
) -> int:
    if budget_regime == "generous":
        return 3
    if budget_regime == "moderate":
        return 2
    return 1


def _typed_memory_problem_features(
    features: ProblemFeatures,
    *,
    descriptors: list[VariableDescriptor],
    bandit_reward: float,
    hybrid_inner_strategy: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "dimensions": features.dimensions,
        "avg_range": features.avg_range,
        "bounded": features.bounded,
        "budget_per_dimension": features.budget_per_dimension,
        "complexity": features.complexity,
    }
    payload.update(descriptor_learning_features(descriptors))
    payload["optimizer_bandit_reward"] = bandit_reward
    if hybrid_inner_strategy is not None:
        payload["hybrid_inner_strategy"] = hybrid_inner_strategy
    return payload


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
    *,
    discrete_descriptors: list[VariableDescriptor] | None = None,
    hybrid_descriptors: list[VariableDescriptor] | None = None,
    rng_seed: int | None = None,
    ablation: AblationConfig | None = None,
) -> OptimizationResult:
    if discrete_descriptors is not None and hybrid_descriptors is not None:
        raise ValueError("Cannot pass both discrete_descriptors and hybrid_descriptors.")

    if hybrid_descriptors is not None and len(bounds) != len(hybrid_descriptors):
        raise ValueError("bounds length must match hybrid_descriptors length.")

    if discrete_descriptors is not None and len(bounds) != len(discrete_descriptors):
        raise ValueError("bounds length must match discrete_descriptors length.")

    ab = coerce(ablation)

    if hybrid_descriptors is not None:
        features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)
        problem_shape = build_problem_shape(
            bounds=bounds,
            max_evaluations=max_evaluations,
        )
        cont_bounds = continuous_bounds_only(hybrid_descriptors)
        sub_features = extract_problem_features(
            bounds=cont_bounds,
            max_evaluations=max_evaluations,
        )
        inner_strategy, inner_confidence, inner_basis = _SELECTOR.select_with_basis(
            features=sub_features,
            domain=domain,
            problem_shape=problem_shape.as_dict(),
            exclude_strategies=frozenset(
                {"discrete_random_neighborhood", "hybrid_outer_random_inner_scipy"}
            ),
            memory_descriptor_mix="mixed",
            ablation=ab,
        )
        strategy_name = "hybrid_outer_random_inner_scipy"
        selection_basis = "hybrid_problem_shape"
        selection_confidence = 1.0
        tuning_priors = (
            compute_solver_tuning_priors(
                features=features,
                budget_regime=problem_shape.budget_regime,
                shape_routing_directive=problem_shape.shape_routing_directive,
                domain=domain,
            )
            if ab.tuning_priors
            else neutral_tuning_priors()
        )
        scipy_result = solve_hybrid_outer_random_inner_scipy(
            objective_function=objective_function,
            descriptors=hybrid_descriptors,
            max_evaluations=max_evaluations,
            inner_strategy=inner_strategy,
            tuning_priors=tuning_priors,
            rng=random.Random(rng_seed) if rng_seed is not None else None,
            ablation=ab,
        )
        best_value = float(scipy_result.fun)
        reward = min(1.0, 1.0 / (1.0 + sqrt(max(0.0, best_value))))
        _SELECTOR.update(strategy_name, reward)
        learning = descriptor_learning_features(hybrid_descriptors)
        _MEMORY.store_optimization_result(
            strategy_name=strategy_name,
            domain=domain,
            problem_features=_typed_memory_problem_features(
                features,
                descriptors=hybrid_descriptors,
                bandit_reward=reward,
                hybrid_inner_strategy=inner_strategy,
            ),
            performance_metrics={
                "final_value": best_value,
                "iterations": int(getattr(scipy_result, "nfev", 0)),
                "time": 0.0,
                "success": bool(getattr(scipy_result, "success", True)),
            },
        )
        solver_success = bool(getattr(scipy_result, "success", True))
        practical_success = solver_success or isfinite(best_value)
        hybrid_attempt_records: list[dict[str, object]] = [
            {
                "attempt": 1,
                "strategy": strategy_name,
                "best_value": best_value,
                "evaluations": int(getattr(scipy_result, "nfev", 0)),
                "success": bool(getattr(scipy_result, "success", True)),
                "budget_allocated": max_evaluations,
            }
        ]
        return OptimizationResult(
            best_solution=list(scipy_result.x),
            best_value=best_value,
            evaluations=int(getattr(scipy_result, "nfev", 0)),
            strategy_used=strategy_name,
            success=practical_success,
            problem_shape=problem_shape.as_dict(),
            explanation={
                "selection_basis": selection_basis,
                "selection_confidence": selection_confidence,
                "domain": domain,
                "strategy_used": strategy_name,
                "shape_routing_directive": problem_shape.shape_routing_directive,
                "shape_routing_score": problem_shape.shape_routing_score,
                "attempt_limit": 1,
                "attempts": hybrid_attempt_records,
                "tuning_priors": tuning_priors,
                "adaptation": {
                    "budget_regime": problem_shape.budget_regime,
                    "complexity_hint": problem_shape.complexity_hint,
                    "problem_complexity": features.complexity,
                    "problem_dimensions": features.dimensions,
                    "problem_budget_per_dimension": features.budget_per_dimension,
                    "global_evaluation_budget": max_evaluations,
                    "planned_strategies": [strategy_name],
                    "winning_attempt": 1,
                    "hybrid_inner_strategy": inner_strategy,
                    "hybrid_inner_selection_basis": inner_basis,
                    "hybrid_inner_selection_confidence": inner_confidence,
                    "descriptor_learning": learning,
                },
            },
        )

    if discrete_descriptors is not None:
        features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)
        problem_shape = build_problem_shape(
            bounds=bounds,
            max_evaluations=max_evaluations,
        )
        strategy_name = "discrete_random_neighborhood"
        selection_basis = "discrete_problem_shape"
        selection_confidence = 1.0
        tuning_priors = (
            compute_solver_tuning_priors(
                features=features,
                budget_regime=problem_shape.budget_regime,
                shape_routing_directive=problem_shape.shape_routing_directive,
                domain=domain,
            )
            if ab.tuning_priors
            else neutral_tuning_priors()
        )
        scipy_result = solve_discrete_baseline(
            objective_function=objective_function,
            descriptors=discrete_descriptors,
            max_evaluations=max_evaluations,
            rng=random.Random(rng_seed) if rng_seed is not None else None,
        )
        best_value = float(scipy_result.fun)
        reward = min(1.0, 1.0 / (1.0 + sqrt(max(0.0, best_value))))
        _SELECTOR.update(strategy_name, reward)
        learning = descriptor_learning_features(discrete_descriptors)
        _MEMORY.store_optimization_result(
            strategy_name=strategy_name,
            domain=domain,
            problem_features=_typed_memory_problem_features(
                features,
                descriptors=discrete_descriptors,
                bandit_reward=reward,
            ),
            performance_metrics={
                "final_value": best_value,
                "iterations": int(getattr(scipy_result, "nfev", 0)),
                "time": 0.0,
                "success": bool(getattr(scipy_result, "success", True)),
            },
        )
        solver_success = bool(getattr(scipy_result, "success", True))
        practical_success = solver_success or isfinite(best_value)
        discrete_attempt_records: list[dict[str, object]] = [
            {
                "attempt": 1,
                "strategy": strategy_name,
                "best_value": best_value,
                "evaluations": int(getattr(scipy_result, "nfev", 0)),
                "success": bool(getattr(scipy_result, "success", True)),
                "budget_allocated": max_evaluations,
            }
        ]
        return OptimizationResult(
            best_solution=list(scipy_result.x),
            best_value=best_value,
            evaluations=int(getattr(scipy_result, "nfev", 0)),
            strategy_used=strategy_name,
            success=practical_success,
            problem_shape=problem_shape.as_dict(),
            explanation={
                "selection_basis": selection_basis,
                "selection_confidence": selection_confidence,
                "domain": domain,
                "strategy_used": strategy_name,
                "shape_routing_directive": problem_shape.shape_routing_directive,
                "shape_routing_score": problem_shape.shape_routing_score,
                "attempt_limit": 1,
                "attempts": discrete_attempt_records,
                "tuning_priors": tuning_priors,
                "adaptation": {
                    "budget_regime": problem_shape.budget_regime,
                    "complexity_hint": problem_shape.complexity_hint,
                    "problem_complexity": features.complexity,
                    "problem_dimensions": features.dimensions,
                    "problem_budget_per_dimension": features.budget_per_dimension,
                    "global_evaluation_budget": max_evaluations,
                    "planned_strategies": [strategy_name],
                    "winning_attempt": 1,
                    "descriptor_learning": learning,
                },
            },
        )

    features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)
    problem_shape = build_problem_shape(
        bounds=bounds,
        max_evaluations=max_evaluations,
    )
    strategy_name, selection_confidence, selection_basis = _SELECTOR.select_with_basis(
        features=features,
        domain=domain,
        problem_shape=problem_shape.as_dict(),
        exclude_strategies=frozenset(
            {"discrete_random_neighborhood", "hybrid_outer_random_inner_scipy"}
        ),
        ablation=ab,
    )
    tuning_priors = (
        compute_solver_tuning_priors(
            features=features,
            budget_regime=problem_shape.budget_regime,
            shape_routing_directive=problem_shape.shape_routing_directive,
            domain=domain,
        )
        if ab.tuning_priors
        else neutral_tuning_priors()
    )
    attempt_limit = (
        _attempt_budget(
            max_evaluations=max_evaluations,
            budget_regime=problem_shape.budget_regime,
        )
        if ab.autodidactic_loop
        else 1
    )
    per_attempt_budget = max(20, max_evaluations // attempt_limit)
    raw_budget_multiplier = tuning_priors["budget_multiplier"]
    budget_multiplier = (
        float(raw_budget_multiplier)
        if isinstance(raw_budget_multiplier, (int, float))
        else 1.0
    )
    attempt_plan = [strategy_name]
    while len(attempt_plan) < attempt_limit:
        attempt_plan.append(_fallback_strategy(attempt_plan[-1]))

    best_result = None
    best_strategy = strategy_name
    winning_attempt_index = 1
    attempt_records: list[dict[str, object]] = []
    for idx, attempt_strategy in enumerate(attempt_plan, start=1):
        effective_budget = max(
            20,
            int(round(per_attempt_budget * budget_multiplier)),
        )
        scipy_result = solve_with_strategy(
            strategy=attempt_strategy,
            objective_function=objective_function,
            bounds=bounds,
            max_evaluations=effective_budget,
            tuning_priors=tuning_priors,
        )
        value = float(scipy_result.fun)
        attempt_records.append(
            {
                "attempt": idx,
                "strategy": attempt_strategy,
                "best_value": value,
                "evaluations": int(getattr(scipy_result, "nfev", 0)),
                "success": bool(getattr(scipy_result, "success", True)),
                "budget_allocated": effective_budget,
            }
        )
        if best_result is None or value < float(best_result.fun):
            best_result = scipy_result
            best_strategy = attempt_strategy
            winning_attempt_index = idx

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
        problem_shape=problem_shape.as_dict(),
        explanation={
            "selection_basis": selection_basis,
            "selection_confidence": selection_confidence,
            "domain": domain,
            "strategy_used": best_strategy,
            "shape_routing_directive": problem_shape.shape_routing_directive,
            "shape_routing_score": problem_shape.shape_routing_score,
            "attempt_limit": attempt_limit,
            "attempts": attempt_records,
            "tuning_priors": tuning_priors,
            "adaptation": {
                "budget_regime": problem_shape.budget_regime,
                "complexity_hint": problem_shape.complexity_hint,
                "problem_complexity": features.complexity,
                "problem_dimensions": features.dimensions,
                "problem_budget_per_dimension": features.budget_per_dimension,
                "global_evaluation_budget": max_evaluations,
                "planned_strategies": list(attempt_plan),
                "winning_attempt": winning_attempt_index,
            },
        },
    )
