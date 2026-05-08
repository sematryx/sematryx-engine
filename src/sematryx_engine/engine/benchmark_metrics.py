"""Reusable selection-quality metrics for domain benchmarks and trend reports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


@dataclass(frozen=True, slots=True)
class SelectionBenchmarkResult:
    """Cold or warm run statistics for a single domain scenario."""

    domain: str
    mode: str
    hit_rate: float
    mean_confidence: float
    runs: int
    target_strategy: str | None


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
        "version": 1,
        "scenarios": {
            "rugged_search": {"cold": row(rugged_cold), "warm": row(rugged_warm)},
            "high_dimensional": {"cold": row(hd_cold), "warm": row(hd_warm)},
        },
    }
