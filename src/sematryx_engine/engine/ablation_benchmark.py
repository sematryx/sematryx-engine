"""Ablation matrix runner.

Runs the same scenario under the all-on baseline and under each single-knob-off
configuration, then computes a Mann-Whitney U verdict per (scenario, knob). See
ADR-0024 for the methodology and verdict rule.

The optimizer reads through module-level singletons (``_MEMORY`` / ``_SELECTOR``); the
runner replaces them with fresh tmp-rooted instances per cell so seeds and ablations do
not contaminate each other. The global ``random`` state is reseeded before each call
since the Thompson-sampling bandit draws through it.

**Methodology caveat — memory-dependent features.** Each cell starts with an empty
memory store and a fresh bandit, which means the ``memory_override`` knob and (to a
lesser extent) the ``descriptor_mix_memory`` knob cannot fire — they need
``usage_count >= 3`` of prior runs in the same domain to trigger. The trade-off is
deliberate (avoids cross-cell contamination from seed ordering) but it means those two
knobs will read as ``no effect`` under the current default scenarios. A future
methodology refinement should add a per-scenario warmup phase that seeds memory with N
prior runs before measurement; until then, those two knobs are measured by their
fallback behaviour, not their effect on cold-start runs.
"""

from __future__ import annotations

import random
import statistics
import tempfile
import time
from collections.abc import Callable, Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scipy.stats import mannwhitneyu

from sematryx_engine.api.client import optimize
from sematryx_engine.api.models import OptimizationResult
from sematryx_engine.engine import optimizer as optimizer_module
from sematryx_engine.engine.ablation import KNOB_NAMES, AblationConfig
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory

ALL_ON = "all_on"


@dataclass(frozen=True, slots=True)
class AblationScenario:
    """One benchmark scenario. ``build_kwargs(seed)`` returns the kwargs for ``optimize``."""

    name: str
    build_kwargs: Callable[[int], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class CellResult:
    """Raw per-seed metrics for one (scenario, knob) cell."""

    scenario: str
    knob: str
    final_values: list[float]
    successes: list[bool]
    evaluations: list[int]
    wall_times_s: list[float]
    strategies: list[str]

    @property
    def n_seeds(self) -> int:
        return len(self.final_values)

    @property
    def median_final_value(self) -> float:
        return statistics.median(self.final_values)

    @property
    def success_rate(self) -> float:
        return sum(1 for s in self.successes if s) / max(1, len(self.successes))


@dataclass(frozen=True, slots=True)
class Verdict:
    """Per (scenario, knob) verdict from the Mann-Whitney U test against all-on."""

    scenario: str
    knob: str
    n_seeds: int
    baseline_median: float
    knob_off_median: float
    delta_median_pct: float
    p_value: float
    verdict: str  # "feature helps" | "no effect" | "regression"


@dataclass(frozen=True, slots=True)
class AblationMatrixResult:
    cells: dict[tuple[str, str], CellResult]  # keyed by (scenario, knob), "all_on" for baseline
    verdicts: list[Verdict]
    seeds: list[int]
    knobs: list[str]
    scenarios: list[str]
    extras: dict[str, Any] = field(default_factory=dict)


@contextmanager
def _isolated_singletons(root: Path) -> Generator[None, None, None]:
    """Replace optimizer module-level memory + selector with fresh tmp-rooted instances."""
    root.mkdir(parents=True, exist_ok=True)
    memory = LocalStrategyMemory(root / "strategy_memory.db")
    selector = StrategySelector(
        memory=memory,
        bandit_state_path=root / "bandit_state.json",
    )
    prev_memory = optimizer_module._MEMORY
    prev_selector = optimizer_module._SELECTOR
    optimizer_module._MEMORY = memory
    optimizer_module._SELECTOR = selector
    try:
        yield
    finally:
        optimizer_module._MEMORY = prev_memory
        optimizer_module._SELECTOR = prev_selector


def _config_for(knob: str) -> AblationConfig:
    if knob == ALL_ON:
        return AblationConfig.default()
    return AblationConfig.default().with_off(knob)


def _classify(delta_pct: float, p_value: float) -> str:
    """ADR-0024 §3 verdict rule: direction + significance, no magnitude threshold."""
    if p_value >= 0.05:
        return "no effect"
    if delta_pct > 0:
        return "feature helps"
    if delta_pct < 0:
        return "regression"
    return "no effect"


def _run_one(
    scenario: AblationScenario,
    seed: int,
    config: AblationConfig,
    isolation_root: Path,
) -> tuple[OptimizationResult, float]:
    with _isolated_singletons(isolation_root):
        random.seed(seed)
        kwargs = scenario.build_kwargs(seed)
        kwargs["ablation"] = config
        kwargs.setdefault("rng_seed", seed)
        t0 = time.perf_counter()
        result = optimize(**kwargs)
        wall = time.perf_counter() - t0
    return result, wall


def run_ablation_matrix(
    scenarios: list[AblationScenario],
    seeds: list[int],
    knobs: Iterable[str] | None = None,
    isolation_root: Path | None = None,
) -> AblationMatrixResult:
    """Run the (scenarios × {all-on} ∪ knobs × seeds) grid and return raw + verdicts."""
    knob_list = sorted(KNOB_NAMES) if knobs is None else sorted(set(knobs))
    for knob in knob_list:
        if knob not in KNOB_NAMES:
            raise ValueError(f"Unknown ablation knob: {knob!r}")

    if isolation_root is None:
        tmp_handle = tempfile.TemporaryDirectory(prefix="ablation_")
        root = Path(tmp_handle.name)
    else:
        tmp_handle = None
        root = isolation_root

    cells: dict[tuple[str, str], CellResult] = {}

    def collect(scenario_name: str, knob: str, seeds_used: list[int]) -> CellResult:
        finals: list[float] = []
        successes: list[bool] = []
        evals: list[int] = []
        walls: list[float] = []
        strategies: list[str] = []
        config = _config_for(knob)
        for seed in seeds_used:
            scenario = next(s for s in scenarios if s.name == scenario_name)
            cell_dir = root / scenario_name / knob / f"seed_{seed}"
            result, wall = _run_one(scenario, seed, config, cell_dir)
            finals.append(float(result.best_value))
            successes.append(bool(result.success))
            evals.append(int(result.evaluations))
            walls.append(wall)
            strategies.append(str(result.strategy_used))
        return CellResult(
            scenario=scenario_name,
            knob=knob,
            final_values=finals,
            successes=successes,
            evaluations=evals,
            wall_times_s=walls,
            strategies=strategies,
        )

    try:
        for scenario in scenarios:
            cells[(scenario.name, ALL_ON)] = collect(scenario.name, ALL_ON, seeds)
            for knob in knob_list:
                cells[(scenario.name, knob)] = collect(scenario.name, knob, seeds)
    finally:
        if tmp_handle is not None:
            tmp_handle.cleanup()

    verdicts: list[Verdict] = []
    for scenario in scenarios:
        baseline = cells[(scenario.name, ALL_ON)]
        baseline_median = baseline.median_final_value
        for knob in knob_list:
            off = cells[(scenario.name, knob)]
            off_median = off.median_final_value
            # Δ = (off - baseline) / |baseline| × 100, sign-preserved.
            denom = abs(baseline_median) if baseline_median != 0 else 1.0
            delta_pct = (off_median - baseline_median) / denom * 100.0
            try:
                u_stat = mannwhitneyu(
                    off.final_values,
                    baseline.final_values,
                    alternative="two-sided",
                )
                p_value = float(u_stat.pvalue)
            except ValueError:
                # All values tied — no statistical signal.
                p_value = 1.0
            verdicts.append(
                Verdict(
                    scenario=scenario.name,
                    knob=knob,
                    n_seeds=len(seeds),
                    baseline_median=baseline_median,
                    knob_off_median=off_median,
                    delta_median_pct=delta_pct,
                    p_value=p_value,
                    verdict=_classify(delta_pct, p_value),
                )
            )

    return AblationMatrixResult(
        cells=cells,
        verdicts=verdicts,
        seeds=list(seeds),
        knobs=knob_list,
        scenarios=[s.name for s in scenarios],
    )


# ---------------------------------------------------------------------------
# Default scenario set
# ---------------------------------------------------------------------------


def _sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def _rugged_multimodal(x: list[float]) -> float:
    """Sum of shifted squares + sinusoidal ripples — many local minima, one global."""
    import math

    total = 0.0
    for i, v in enumerate(x):
        shift = 0.3 * (i + 1)
        total += (v - shift) ** 2 + 0.6 * math.sin(3.5 * v) ** 2
    return total


def _knapsack_like(x: list[float]) -> float:
    """Integer-only quadratic — exercises the discrete path."""
    target = [2, -1, 3, 0, 1]
    return sum((int(round(v)) - t) ** 2 for v, t in zip(x, target, strict=False))


def _hybrid_assignment(x: list[float]) -> float:
    """Mixed discrete + continuous with cross-term — exercises the hybrid path."""
    disc = int(round(x[0]))  # integer
    cat = int(round(x[1]))   # categorical index
    cont = x[2:]
    base = sum(v * v for v in cont)
    discrete_penalty = (disc - 2) ** 2 + (cat - 1) ** 2
    cross = 0.2 * abs(disc) * sum(abs(v) for v in cont)
    return base + discrete_penalty + cross


def default_scenarios() -> list[AblationScenario]:
    """Four scenarios: smooth continuous, rugged-multimodal (topology-sensitive),
    discrete-only, and mixed hybrid. Covers all three optimizer code paths plus a case
    where topology routing should matter."""

    def sphere_smooth_kwargs(_seed: int) -> dict[str, Any]:
        return {
            "objective_function": _sphere,
            "bounds": [(-2.0, 2.0)] * 4,
            "max_evaluations": 200,
            "domain": "ablation_sphere_smooth",
        }

    def rugged_multimodal_kwargs(_seed: int) -> dict[str, Any]:
        return {
            "objective_function": _rugged_multimodal,
            "bounds": [(-5.0, 5.0)] * 8,
            "max_evaluations": 400,
            "domain": "ablation_rugged_multimodal",
        }

    def discrete_knapsack_kwargs(_seed: int) -> dict[str, Any]:
        return {
            "objective_function": _knapsack_like,
            "variable_descriptors": [
                {"name": f"x{i}", "kind": "integer", "low": -4, "high": 4}
                for i in range(5)
            ],
            "max_evaluations": 250,
            "domain": "ablation_discrete_knapsack",
        }

    def hybrid_mixed_kwargs(_seed: int) -> dict[str, Any]:
        return {
            "objective_function": _hybrid_assignment,
            "variable_descriptors": [
                {"name": "i", "kind": "integer", "low": 0, "high": 5},
                {"name": "c", "kind": "categorical", "categories": ["p", "q", "r"]},
                {"name": "x", "kind": "continuous", "low": -3.0, "high": 3.0},
                {"name": "y", "kind": "continuous", "low": -2.0, "high": 2.0},
                {"name": "z", "kind": "continuous", "low": -1.0, "high": 1.0},
            ],
            "max_evaluations": 320,
            "domain": "ablation_hybrid_mixed",
        }

    return [
        AblationScenario("sphere_smooth", sphere_smooth_kwargs),
        AblationScenario("rugged_multimodal_8d", rugged_multimodal_kwargs),
        AblationScenario("discrete_knapsack", discrete_knapsack_kwargs),
        AblationScenario("hybrid_mixed", hybrid_mixed_kwargs),
    ]


def default_light_seeds() -> list[int]:
    """Light matrix seed set (N=20). CI-eligible."""
    return list(range(1001, 1021))


def default_heavy_seeds() -> list[int]:
    """Heavy matrix seed set (N=100). On-demand only."""
    return list(range(1001, 1101))
