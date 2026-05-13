"""Ablation matrix runner.

Runs the same scenario under the all-on baseline and under each single-knob-off
configuration, then computes a Mann-Whitney U verdict per (scenario, knob). See
ADR-0024 for the methodology and verdict rule.

The optimizer reads through module-level singletons (``_MEMORY`` / ``_SELECTOR``); the
runner replaces them with fresh tmp-rooted instances per cell so seeds and ablations do
not contaminate each other. The global ``random`` state is reseeded before each call
since the Thompson-sampling bandit draws through it.

Scenarios with ``warmup_runs > 0`` run that many ``optimize(...)`` calls under
``AblationConfig.default()`` before each measurement cell, snapshotting the resulting
``strategy_memory.db`` + ``bandit_state.json``. Every knob cell at that (scenario, seed)
copies the snapshot into a fresh isolation directory before measurement — cells stay
independent (no seed-ordering or knob-ordering contamination), but history-dependent
knobs (``memory_override``, ``descriptor_mix_memory``, ``continuous_bandit``) can fire.
See ADR-0025.
"""

from __future__ import annotations

import random
import shutil
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
    """One benchmark scenario. ``build_kwargs(seed)`` returns the kwargs for ``optimize``.

    ``warmup_runs`` (default 0) pre-populates `_MEMORY` and `_SELECTOR` with that many
    `optimize(...)` calls under `AblationConfig.default()` before each measurement cell.
    Set this > 0 for scenarios where history-dependent knobs (``memory_override``,
    ``descriptor_mix_memory``, ``continuous_bandit``) need to fire. Leave at 0 for
    scenarios that must be measured cold (e.g. shape-routing-firing scenarios where memory
    override would shadow the routing override). See ADR-0025.
    """

    name: str
    build_kwargs: Callable[[int], dict[str, Any]]
    warmup_runs: int = 0


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


def _build_warmup_snapshot(
    scenario: AblationScenario,
    seed: int,
    snapshot_root: Path,
) -> Path:
    """Run scenario.warmup_runs into a snapshot dir; return the dir.

    Warmup uses derived seeds (``seed * 1000 + w``) disjoint from measurement seed space
    (1001-1100) and runs under ``AblationConfig.default()`` to populate memory + bandit.
    The resulting ``strategy_memory.db`` and ``bandit_state.json`` are reused across every
    knob cell at this (scenario, seed) via file copy (see ``_run_one``).
    """
    snapshot_root.mkdir(parents=True, exist_ok=True)
    if scenario.warmup_runs <= 0:
        return snapshot_root  # empty snapshot = current cold-cell behaviour
    with _isolated_singletons(snapshot_root):
        for w in range(scenario.warmup_runs):
            warmup_seed = seed * 1000 + w
            random.seed(warmup_seed)
            kwargs = scenario.build_kwargs(warmup_seed)
            kwargs["ablation"] = AblationConfig.default()
            kwargs.setdefault("rng_seed", warmup_seed)
            optimize(**kwargs)
    return snapshot_root


def _seed_isolation_from_snapshot(snapshot_root: Path, cell_root: Path) -> None:
    """Copy warmup artefacts (``strategy_memory.db``, ``bandit_state.json``) from a
    cached snapshot into a fresh per-cell isolation directory before measurement."""
    cell_root.mkdir(parents=True, exist_ok=True)
    for name in ("strategy_memory.db", "bandit_state.json"):
        src = snapshot_root / name
        if src.exists():
            shutil.copy2(src, cell_root / name)


def _run_one(
    scenario: AblationScenario,
    seed: int,
    config: AblationConfig,
    snapshot_root: Path,
    isolation_root: Path,
) -> tuple[OptimizationResult, float]:
    _seed_isolation_from_snapshot(snapshot_root, isolation_root)
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

    # Build all warmup snapshots up front (one per scenario × seed). Knob cells reuse them
    # via copy so each cell still runs against an isolated, identical starting state.
    snapshots: dict[tuple[str, int], Path] = {}
    for scenario in scenarios:
        for seed in seeds:
            snapshot_root = root / "warmup_snapshots" / scenario.name / f"seed_{seed}"
            snapshots[(scenario.name, seed)] = _build_warmup_snapshot(
                scenario, seed, snapshot_root
            )

    def collect(scenario_name: str, knob: str, seeds_used: list[int]) -> CellResult:
        finals: list[float] = []
        successes: list[bool] = []
        evals: list[int] = []
        walls: list[float] = []
        strategies: list[str] = []
        config = _config_for(knob)
        scenario = next(s for s in scenarios if s.name == scenario_name)
        for seed in seeds_used:
            cell_dir = root / scenario_name / knob / f"seed_{seed}"
            snapshot_root = snapshots[(scenario_name, seed)]
            result, wall = _run_one(scenario, seed, config, snapshot_root, cell_dir)
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
    """Mixed discrete + continuous with cross-term — exercises the hybrid path.

    Known to floor at median=1 in baseline `v1` (discrete shell search misses optimum
    (disc=2, cat=1) by 1 consistently). `_hybrid_smooth` below is the separating version.
    """
    disc = int(round(x[0]))  # integer
    cat = int(round(x[1]))   # categorical index
    cont = x[2:]
    base = sum(v * v for v in cont)
    discrete_penalty = (disc - 2) ** 2 + (cat - 1) ** 2
    cross = 0.2 * abs(disc) * sum(abs(v) for v in cont)
    return base + discrete_penalty + cross


def _hybrid_smooth(x: list[float]) -> float:
    """4 integers ∈ [0,5] (1296 shells) + 2 continuous, smooth quadratic.

    Designed so the discrete shell choice creates a gradient that LCB acquisition can
    follow but uniform shell sampling cannot. The 4 integers give 6^4 = 1296 shells; an
    outer budget of ~20 exploration steps visits a tiny fraction, so the visit allocation
    strategy meaningfully affects outcomes.
    """
    target = (2, 3, 1, 4)
    disc_cost = sum((int(round(x[i])) - target[i]) ** 2 for i in range(4))
    cont_cost = sum(v * v for v in x[4:])
    return disc_cost + cont_cost


def default_scenarios() -> list[AblationScenario]:
    """Scenarios sized so every ablation knob has at least one cell where it can fire.

    Coverage map (see ADR-0025):

    - ``sphere_smooth``: trivial continuous; reference for "feature doesn't matter".
    - ``rugged_multimodal_8d``: warmed (``warmup_runs=5``) — exercises ``memory_override``,
      ``continuous_bandit`` post-warmup; also where ``autodidactic_loop`` and
      ``tuning_priors`` showed effect in baseline v1.
    - ``discrete_knapsack``: warmed; discrete-bandit and discrete-memory test.
    - ``hybrid_separating``: warmed; ``hybrid_outer_acquisition`` /
      ``hybrid_outer_refinement`` / ``descriptor_mix_memory`` test target. Replaces the
      floor-converging ``hybrid_mixed`` for these knobs.
    - ``shape_routing_firing_current``: cold (``warmup_runs=0``) by design — 13D + tight
      budget pushes ``shape_routing_score`` past 0.75 and the shape-routing override must
      fire ahead of any warmed memory override.
    - ``hybrid_mixed``: retained as legacy reference (floor-converging).
    """

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

    def hybrid_separating_kwargs(_seed: int) -> dict[str, Any]:
        return {
            "objective_function": _hybrid_smooth,
            "variable_descriptors": [
                {"name": f"i{i}", "kind": "integer", "low": 0, "high": 5}
                for i in range(4)
            ] + [
                {"name": "c1", "kind": "continuous", "low": -3.0, "high": 3.0},
                {"name": "c2", "kind": "continuous", "low": -3.0, "high": 3.0},
            ],
            "max_evaluations": 600,
            "domain": "ablation_hybrid_separating",
        }

    def shape_routing_firing_current_kwargs(_seed: int) -> dict[str, Any]:
        # 13D, max_evaluations=600 → budget_per_dimension=46.15 → tight regime
        # → shape_routing_score = 0.45·1.0 + 0.35·1.0 + 0.20·0 = 0.80 → directive=aggressive
        # → shape-routing override fires under current heuristic. See ADR-0025, ADR-0026.
        return {
            "objective_function": _rugged_multimodal,
            "bounds": [(-5.0, 5.0)] * 13,
            "max_evaluations": 600,
            "domain": "ablation_shape_routing_firing_current",
        }

    # warmup_runs=10 chosen so that Thompson sampling has enough updates to concentrate on
    # the dominant strategy (memory_override fires at usage_count >= 3). With rugged objectives
    # and reward variance, 5 warmup runs scatter picks across ~5 strategies; 10 reliably gets
    # at least one strategy past the threshold on most seeds. See ADR-0025.
    return [
        AblationScenario("sphere_smooth", sphere_smooth_kwargs, warmup_runs=0),
        AblationScenario("rugged_multimodal_8d", rugged_multimodal_kwargs, warmup_runs=10),
        AblationScenario("discrete_knapsack", discrete_knapsack_kwargs, warmup_runs=10),
        AblationScenario("hybrid_mixed", hybrid_mixed_kwargs, warmup_runs=0),
        AblationScenario("hybrid_separating", hybrid_separating_kwargs, warmup_runs=10),
        AblationScenario("shape_routing_firing_current", shape_routing_firing_current_kwargs, warmup_runs=0),
    ]


def default_light_seeds() -> list[int]:
    """Light matrix seed set (N=20). CI-eligible."""
    return list(range(1001, 1021))


def default_heavy_seeds() -> list[int]:
    """Heavy matrix seed set (N=100). On-demand only."""
    return list(range(1001, 1101))
