"""Light integration test for the ablation harness.

Smaller than the actual `make ablation` matrix so it can run in the standard test loop;
the goal is to catch wiring breakage (singletons not isolated, knobs not threaded, report
schema drift), not to produce verdict evidence. The pre-Stage-4 baseline lives under
`docs/process/verification/ablation/` and is produced by `make ablation-full`.
"""

from __future__ import annotations

import json
from pathlib import Path

from sematryx_engine.engine.ablation import KNOB_NAMES
from sematryx_engine.engine.ablation_benchmark import (
    ALL_ON,
    AblationScenario,
    _build_warmup_snapshot,
    default_scenarios,
    run_ablation_matrix,
)
from sematryx_engine.engine.topology import build_topology_artifact
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def test_light_matrix_runs_to_completion(tmp_path: Path) -> None:
    scenarios = default_scenarios()[:2]  # sphere + rugged
    seeds = [101, 102, 103, 104]
    result = run_ablation_matrix(
        scenarios=scenarios,
        seeds=seeds,
        isolation_root=tmp_path,
    )

    # Every (scenario, all_on) and (scenario, knob) cell is populated with N samples each.
    expected_keys = {(s.name, ALL_ON) for s in scenarios} | {
        (s.name, k) for s in scenarios for k in KNOB_NAMES
    }
    assert set(result.cells.keys()) == expected_keys
    for cell in result.cells.values():
        assert cell.n_seeds == len(seeds)
        assert len(cell.final_values) == len(seeds)
        assert len(cell.wall_times_s) == len(seeds)

    # One verdict per (scenario, knob) — never for the all-on baseline itself.
    expected_verdict_pairs = {(s.name, k) for s in scenarios for k in KNOB_NAMES}
    actual_verdict_pairs = {(v.scenario, v.knob) for v in result.verdicts}
    assert actual_verdict_pairs == expected_verdict_pairs

    valid = {"feature helps", "no effect", "regression"}
    for v in result.verdicts:
        assert v.verdict in valid, v


def test_report_generator_round_trip(tmp_path: Path, monkeypatch) -> None:
    """The script's JSON output must parse, carry the schema_version, and include every cell."""
    import scripts.generate_ablation_report as gen_module

    monkeypatch.setattr(gen_module, "default_light_seeds", lambda: [201, 202, 203])
    monkeypatch.setattr(
        gen_module,
        "default_scenarios",
        lambda: default_scenarios()[:1],  # sphere only — fastest path through the runner
    )

    output_dir = tmp_path / "report"
    monkeypatch.setattr(
        "sys.argv",
        [
            "generate_ablation_report.py",
            "--mode", "light",
            "--output-dir", str(output_dir),
            "--label", "test",
        ],
    )
    exit_code = gen_module.main()
    assert exit_code == 0

    json_path = output_dir / "ablation_test.json"
    md_path = output_dir / "ablation_test.md"
    assert json_path.exists()
    assert md_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["mode"] == "light"
    assert payload["matrix"]["scenarios"] == ["sphere_smooth"]
    assert set(payload["matrix"]["knobs"]) == set(KNOB_NAMES)
    # one all-on cell + one per knob.
    assert len(payload["cells"]) == 1 + len(KNOB_NAMES)
    # one verdict per knob, never for all-on.
    assert len(payload["verdicts"]) == len(KNOB_NAMES)
    for verdict in payload["verdicts"]:
        assert verdict["knob"] != ALL_ON
        assert verdict["verdict"] in {"feature helps", "no effect", "regression"}

    md_text = md_path.read_text(encoding="utf-8")
    assert "Ablation matrix report" in md_text
    assert "sphere_smooth" in md_text
    for knob in KNOB_NAMES:
        assert knob in md_text


def test_warmup_populates_memory_for_override_firing(tmp_path: Path) -> None:
    """Warmup must leave memory dense enough on most seeds for ``memory_override`` to fire
    (top strategy ``usage_count >= 3``). Tests across several seeds since Thompson sampling
    has run-to-run variance — assert that at least 60% of warmup snapshots clear the
    threshold. Guards against silent regressions in the warmup snapshot pipeline."""
    rugged = next(s for s in default_scenarios() if s.name == "rugged_multimodal_8d")
    assert rugged.warmup_runs >= 10

    seeds = [101, 102, 103, 104, 105]
    firing_count = 0
    for seed in seeds:
        snapshot_dir = _build_warmup_snapshot(rugged, seed, tmp_path / f"snap_{seed}")
        memory = LocalStrategyMemory(snapshot_dir / "strategy_memory.db")
        recs = memory.get_strategy_recommendations(
            domain="ablation_rugged_multimodal", limit=5
        )
        if recs and max(r.usage_count for r in recs) >= 3:
            firing_count += 1

    assert firing_count >= int(0.6 * len(seeds)), (
        f"warmup populates memory_override threshold on only {firing_count}/{len(seeds)} "
        f"seeds — expected at least 60% to clear usage_count >= 3"
    )


def test_topology_firing_scenario_actually_fires() -> None:
    """`topology_firing_current` must cross the override gate
    (`score >= 0.75` or `directive == 'aggressive'`). Otherwise topology_routing remains
    unmeasured and the scenario is dead weight."""
    firing = next(s for s in default_scenarios() if s.name == "topology_firing_current")
    kwargs = firing.build_kwargs(101)
    artifact = build_topology_artifact(
        bounds=kwargs["bounds"],
        max_evaluations=kwargs["max_evaluations"],
    )
    fires = (
        artifact.tunneling_directive == "aggressive"
        or artifact.physarum_tunneling_score >= 0.75
    )
    assert fires, (
        f"topology_firing_current does not trigger the override gate: "
        f"score={artifact.physarum_tunneling_score}, directive={artifact.tunneling_directive}"
    )


def test_warmup_runs_zero_byte_identical_to_no_warmup(tmp_path: Path) -> None:
    """A scenario declared with ``warmup_runs=0`` must produce the same snapshot dir state
    as one that never ran warmup at all (no spurious db/json files in the snapshot)."""
    cold = AblationScenario(
        name="cold",
        build_kwargs=lambda _s: {
            "objective_function": lambda x: sum(v * v for v in x),
            "bounds": [(-1.0, 1.0), (-1.0, 1.0)],
            "max_evaluations": 50,
            "domain": "cold_test",
        },
        warmup_runs=0,
    )
    snap = _build_warmup_snapshot(cold, 42, tmp_path / "cold")
    assert snap.exists()
    assert not (snap / "strategy_memory.db").exists()
    assert not (snap / "bandit_state.json").exists()
