"""Reusable selection-quality metrics for domain benchmarks and trend reports."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from sematryx_engine.api.variable_descriptors import normalize_variable_descriptors
from sematryx_engine.engine.discrete_benchmark_scenarios import (
    assignment_2x2_penalty_objective,
    assignment_2x2_specs,
    assignment_2x2_variable_descriptors,
    knapsack_01_penalty_objective,
    knapsack_01_small_specs,
    knapsack_01_variable_descriptors,
)
from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory
from sematryx_engine.solvers.discrete_solvers import solve_discrete_baseline
from sematryx_engine.solvers.strategy_dispatch import solve_with_strategy


@dataclass(frozen=True, slots=True)
class SelectionBenchmarkResult:
    """Cold or warm run statistics for a single domain scenario."""

    domain: str
    mode: str
    hit_rate: float
    mean_confidence: float
    runs: int
    target_strategy: str | None


@dataclass(frozen=True, slots=True)
class ObjectiveBenchmarkResult:
    """End-to-end objective quality from one isolated optimize-style run."""

    scenario_name: str
    best_value: float
    evaluations: int
    strategy_used: str
    dimensions: int
    domain: str


def sphere_objective(x: list[float]) -> float:
    """Classic sphere sum of squares."""
    return sum(v * v for v in x)


def run_objective_benchmark_isolated(
    *,
    scenario_name: str,
    bounds: list[tuple[float, float]],
    max_evaluations: int,
    domain: str,
    memory_path: Path,
    bandit_state_path: Path | None,
    objective_seed: int,
) -> ObjectiveBenchmarkResult:
    """One scipy-backed minimize matching optimizer wiring but isolated persistence."""
    import random

    random.seed(objective_seed)
    memory = LocalStrategyMemory(memory_path)
    selector = StrategySelector(memory=memory, bandit_state_path=bandit_state_path)
    features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)
    strategy_name, _confidence = selector.select(features, domain=domain)
    scipy_result = solve_with_strategy(
        strategy=strategy_name,
        objective_function=sphere_objective,
        bounds=bounds,
        max_evaluations=max_evaluations,
    )
    return ObjectiveBenchmarkResult(
        scenario_name=scenario_name,
        best_value=float(scipy_result.fun),
        evaluations=int(getattr(scipy_result, "nfev", 0)),
        strategy_used=strategy_name,
        dimensions=len(bounds),
        domain=domain,
    )


def collect_discrete_objective_benchmark_snapshot() -> dict[str, dict[str, object]]:
    """Isolated discrete solver runs matching Stage 3 validation scenario seeds."""

    def row(obr: ObjectiveBenchmarkResult) -> dict[str, object]:
        return {
            "scenario_name": obr.scenario_name,
            "best_value": obr.best_value,
            "evaluations": obr.evaluations,
            "strategy_used": obr.strategy_used,
            "dimensions": obr.dimensions,
            "domain": obr.domain,
        }

    weights, values, capacity, _opt_profit = knapsack_01_small_specs()
    kn_desc = normalize_variable_descriptors(knapsack_01_variable_descriptors())
    kn_obj = knapsack_01_penalty_objective(weights, values, capacity)
    kn_res = solve_discrete_baseline(
        kn_obj,
        kn_desc,
        max_evaluations=1800,
        rng=random.Random(20260111),
    )
    kn_row = ObjectiveBenchmarkResult(
        scenario_name="knapsack01",
        best_value=float(kn_res.fun),
        evaluations=int(getattr(kn_res, "nfev", 0)),
        strategy_used="discrete_random_neighborhood",
        dimensions=len(kn_desc),
        domain="stage3_snapshot_knapsack01",
    )

    cost, _opt_cost = assignment_2x2_specs()
    as_desc = normalize_variable_descriptors(assignment_2x2_variable_descriptors())
    as_obj = assignment_2x2_penalty_objective(cost)
    as_res = solve_discrete_baseline(
        as_obj,
        as_desc,
        max_evaluations=900,
        rng=random.Random(20260112),
    )
    as_row = ObjectiveBenchmarkResult(
        scenario_name="assignment2x2",
        best_value=float(as_res.fun),
        evaluations=int(getattr(as_res, "nfev", 0)),
        strategy_used="discrete_random_neighborhood",
        dimensions=len(as_desc),
        domain="stage3_snapshot_assignment2x2",
    )

    return {"knapsack01": row(kn_row), "assignment2x2": row(as_row)}


def collect_objective_benchmark_snapshot(tmp_path: Path) -> dict[str, dict[str, object]]:
    """Runs reproducible sphere cases with isolated SQLite/bandit files."""

    def row(obr: ObjectiveBenchmarkResult) -> dict[str, object]:
        return {
            "scenario_name": obr.scenario_name,
            "best_value": obr.best_value,
            "evaluations": obr.evaluations,
            "strategy_used": obr.strategy_used,
            "dimensions": obr.dimensions,
            "domain": obr.domain,
        }

    low = run_objective_benchmark_isolated(
        scenario_name="sphere_dim4",
        bounds=[(-5.0, 5.0)] * 4,
        max_evaluations=400,
        domain="objective_sphere_low",
        memory_path=tmp_path / "obj_sphere4_memory.db",
        bandit_state_path=tmp_path / "obj_sphere4_bandit.json",
        objective_seed=101,
    )
    mid = run_objective_benchmark_isolated(
        scenario_name="sphere_dim8",
        bounds=[(-4.0, 4.0)] * 8,
        max_evaluations=600,
        domain="objective_sphere_mid",
        memory_path=tmp_path / "obj_sphere8_memory.db",
        bandit_state_path=tmp_path / "obj_sphere8_bandit.json",
        objective_seed=103,
    )

    merged: dict[str, dict[str, object]] = {
        "sphere_dim4": row(low),
        "sphere_dim8": row(mid),
    }
    merged.update(collect_discrete_objective_benchmark_snapshot())
    return merged


def run_selection_benchmark(
    *,
    domain: str,
    bounds: list[tuple[float, float]],
    max_evaluations: int,
    warm_strategy: str | None,
    warm_count: int,
    runs: int,
    memory_path: Path,
) -> SelectionBenchmarkResult:
    """Measure mean confidence and (if applicable) target-strategy hit rate."""
    memory = LocalStrategyMemory(memory_path)
    if warm_strategy is not None:
        for _ in range(warm_count):
            memory.store_optimization_result(
                strategy_name=warm_strategy,
                domain=domain,
                problem_features={"dimensions": len(bounds)},
                performance_metrics={
                    "final_value": 0.02,
                    "iterations": 50,
                    "time": 0.2,
                    "success": True,
                },
            )

    selector = StrategySelector(memory=memory)
    features = extract_problem_features(bounds=bounds, max_evaluations=max_evaluations)

    target_hits = 0
    confidence_sum = 0.0
    for _ in range(runs):
        strategy, confidence = selector.select(features=features, domain=domain)
        confidence_sum += confidence
        if warm_strategy is not None and strategy == warm_strategy:
            target_hits += 1

    hit_rate = (target_hits / runs) if warm_strategy is not None else 0.0
    mean_confidence = confidence_sum / runs
    mode = "warm" if warm_strategy is not None else "cold"

    return SelectionBenchmarkResult(
        domain=domain,
        mode=mode,
        hit_rate=hit_rate,
        mean_confidence=mean_confidence,
        runs=runs,
        target_strategy=warm_strategy,
    )


def collect_domain_benchmark_snapshot(
    *,
    tmp_path: Path,
    rugged_runs: int = 100,
    high_dim_runs: int = 100,
    discrete_selection_runs: int | None = None,
) -> dict[str, object]:
    """Run standard domain scenarios and return structured metrics for reporting."""
    random.seed(21)
    rugged_cold = run_selection_benchmark(
        domain="rugged_search",
        bounds=[(-9.0, 9.0)] * 6,
        max_evaluations=300,
        warm_strategy=None,
        warm_count=0,
        runs=rugged_runs,
        memory_path=tmp_path / "rugged_cold.db",
    )
    rugged_warm = run_selection_benchmark(
        domain="rugged_search",
        bounds=[(-9.0, 9.0)] * 6,
        max_evaluations=300,
        warm_strategy="scipy_de",
        warm_count=8,
        runs=rugged_runs,
        memory_path=tmp_path / "rugged_warm.db",
    )

    random.seed(37)
    hd_cold = run_selection_benchmark(
        domain="high_dimensional",
        bounds=[(-5.0, 5.0)] * 18,
        max_evaluations=350,
        warm_strategy=None,
        warm_count=0,
        runs=high_dim_runs,
        memory_path=tmp_path / "hd_cold.db",
    )
    hd_warm = run_selection_benchmark(
        domain="high_dimensional",
        bounds=[(-5.0, 5.0)] * 18,
        max_evaluations=350,
        warm_strategy="scipy_dual_annealing",
        warm_count=8,
        runs=high_dim_runs,
        memory_path=tmp_path / "hd_warm.db",
    )

    druns = discrete_selection_runs if discrete_selection_runs is not None else rugged_runs
    random.seed(41)
    dk_cold = run_selection_benchmark(
        domain="stage3_trend_knapsack01",
        bounds=[(0.0, 1.0)] * 4,
        max_evaluations=500,
        warm_strategy=None,
        warm_count=0,
        runs=druns,
        memory_path=tmp_path / "disc_knapsack_cold.db",
    )
    dk_warm = run_selection_benchmark(
        domain="stage3_trend_knapsack01",
        bounds=[(0.0, 1.0)] * 4,
        max_evaluations=500,
        warm_strategy="discrete_random_neighborhood",
        warm_count=8,
        runs=druns,
        memory_path=tmp_path / "disc_knapsack_warm.db",
    )

    random.seed(43)
    da_cold = run_selection_benchmark(
        domain="stage3_trend_assignment2x2",
        bounds=[(0.0, 1.0)] * 2,
        max_evaluations=400,
        warm_strategy=None,
        warm_count=0,
        runs=druns,
        memory_path=tmp_path / "disc_assign_cold.db",
    )
    da_warm = run_selection_benchmark(
        domain="stage3_trend_assignment2x2",
        bounds=[(0.0, 1.0)] * 2,
        max_evaluations=400,
        warm_strategy="discrete_random_neighborhood",
        warm_count=8,
        runs=druns,
        memory_path=tmp_path / "disc_assign_warm.db",
    )

    def row(r: SelectionBenchmarkResult) -> dict[str, object]:
        return {
            "domain": r.domain,
            "mode": r.mode,
            "hit_rate": r.hit_rate,
            "mean_confidence": r.mean_confidence,
            "runs": r.runs,
            "target_strategy": r.target_strategy,
        }

    return {
        "version": 2,
        "scenarios": {
            "rugged_search": {"cold": row(rugged_cold), "warm": row(rugged_warm)},
            "high_dimensional": {"cold": row(hd_cold), "warm": row(hd_warm)},
            "discrete_knapsack": {"cold": row(dk_cold), "warm": row(dk_warm)},
            "discrete_assignment2x2": {"cold": row(da_cold), "warm": row(da_warm)},
        },
        "objectives": collect_objective_benchmark_snapshot(tmp_path),
    }
