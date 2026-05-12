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
    default_scenarios,
    run_ablation_matrix,
)


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
