"""Byte-identity contract: ``ablation=None`` and ``ablation=AblationConfig.default()``
must produce identical results to the pre-PRD-0025 call path for the same seeded inputs.

The optimizer reads through module-level singletons for the bandit + memory store, so each
run replaces those singletons with tmp-path-rooted instances before invoking ``optimize``.
The global ``random`` state is reseeded per run since the Thompson-sampling bandit draws
through it.
"""

from __future__ import annotations

import random
from pathlib import Path

from sematryx_engine import AblationConfig, optimize
from sematryx_engine.engine import optimizer as optimizer_module
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def _isolate_singletons(monkeypatch, tmp_path: Path) -> None:
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")
    selector = StrategySelector(
        memory=memory,
        bandit_state_path=tmp_path / "bandit_state.json",
    )
    monkeypatch.setattr(optimizer_module, "_MEMORY", memory)
    monkeypatch.setattr(optimizer_module, "_SELECTOR", selector)


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def rugged(x: list[float]) -> float:
    return sum(v * v - 0.5 * (v - 1.0) ** 2 for v in x) + 0.1 * sum(abs(v) for v in x)


def _run_continuous(seed: int, ablation: AblationConfig | None, monkeypatch, tmp_path: Path):
    _isolate_singletons(monkeypatch, tmp_path)
    random.seed(seed)
    return optimize(
        objective_function=sphere,
        bounds=[(-3.0, 3.0), (-2.0, 2.0), (-1.0, 1.0), (-4.0, 4.0)],
        max_evaluations=180,
        domain="byte_identity_continuous",
        rng_seed=seed,
        ablation=ablation,
    )


def _run_discrete(seed: int, ablation: AblationConfig | None, monkeypatch, tmp_path: Path):
    _isolate_singletons(monkeypatch, tmp_path)
    random.seed(seed)
    descriptors = [
        {"name": "a", "kind": "integer", "low": 0, "high": 7},
        {"name": "b", "kind": "categorical", "categories": ["x", "y", "z"]},
        {"name": "c", "kind": "integer", "low": -3, "high": 3},
    ]

    def integer_objective(x: list[float]) -> float:
        return sum(v * v for v in x)

    return optimize(
        objective_function=integer_objective,
        variable_descriptors=descriptors,
        max_evaluations=150,
        domain="byte_identity_discrete",
        rng_seed=seed,
        ablation=ablation,
    )


def _run_hybrid(seed: int, ablation: AblationConfig | None, monkeypatch, tmp_path: Path):
    _isolate_singletons(monkeypatch, tmp_path)
    random.seed(seed)
    descriptors = [
        {"name": "i", "kind": "integer", "low": 0, "high": 5},
        {"name": "c", "kind": "categorical", "categories": ["p", "q"]},
        {"name": "x", "kind": "continuous", "low": -2.0, "high": 2.0},
        {"name": "y", "kind": "continuous", "low": -1.0, "high": 1.0},
    ]
    return optimize(
        objective_function=rugged,
        variable_descriptors=descriptors,
        max_evaluations=200,
        domain="byte_identity_hybrid",
        rng_seed=seed,
        ablation=ablation,
    )


def _assert_result_equal(r1, r2) -> None:
    assert r1.best_value == r2.best_value
    assert r1.best_solution == r2.best_solution
    assert r1.evaluations == r2.evaluations
    assert r1.strategy_used == r2.strategy_used
    assert r1.success == r2.success


def test_byte_identity_continuous(monkeypatch, tmp_path: Path) -> None:
    for seed in (7, 21, 101):
        none_run = _run_continuous(seed, None, monkeypatch, tmp_path / f"none_{seed}")
        default_run = _run_continuous(
            seed, AblationConfig.default(), monkeypatch, tmp_path / f"default_{seed}"
        )
        _assert_result_equal(none_run, default_run)


def test_byte_identity_discrete(monkeypatch, tmp_path: Path) -> None:
    for seed in (7, 21, 101):
        none_run = _run_discrete(seed, None, monkeypatch, tmp_path / f"none_{seed}")
        default_run = _run_discrete(
            seed, AblationConfig.default(), monkeypatch, tmp_path / f"default_{seed}"
        )
        _assert_result_equal(none_run, default_run)


def test_byte_identity_hybrid(monkeypatch, tmp_path: Path) -> None:
    for seed in (7, 21, 101):
        none_run = _run_hybrid(seed, None, monkeypatch, tmp_path / f"none_{seed}")
        default_run = _run_hybrid(
            seed, AblationConfig.default(), monkeypatch, tmp_path / f"default_{seed}"
        )
        _assert_result_equal(none_run, default_run)


def test_off_paths_diverge_from_default(monkeypatch, tmp_path: Path) -> None:
    """Sanity: at least one ablation off-path must produce a different trace than the
    all-on default. If every knob is a no-op, the harness can never detect anything."""
    seed = 42
    default_run = _run_continuous(
        seed, AblationConfig.default(), monkeypatch, tmp_path / "default"
    )
    all_off_run = _run_continuous(
        seed, AblationConfig.all_off(), monkeypatch, tmp_path / "all_off"
    )
    # Either the strategy choice or the numeric result must differ. Both being identical
    # would imply the knobs do not actually toggle behaviour at this scenario size.
    diverged = (
        default_run.strategy_used != all_off_run.strategy_used
        or default_run.best_value != all_off_run.best_value
        or default_run.evaluations != all_off_run.evaluations
    )
    assert diverged, (
        f"all-off run matched default run exactly — knobs appear to be no-ops. "
        f"default={default_run.strategy_used}/{default_run.best_value} "
        f"all_off={all_off_run.strategy_used}/{all_off_run.best_value}"
    )
