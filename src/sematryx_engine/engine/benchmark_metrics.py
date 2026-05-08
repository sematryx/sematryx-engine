"""Reusable selection-quality metrics for domain benchmarks and trend reports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory
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


def collect_objective_benchmark_snapshot(tmp_path: Path) -> dict[str, object]:
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

    return {"sphere_dim4": row(low), "sphere_dim8": row(mid)}


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
) -> dict[str, object]:
    """Run standard domain scenarios and return structured metrics for reporting."""
    import random

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
        },
        "objectives": collect_objective_benchmark_snapshot(tmp_path),
    }
