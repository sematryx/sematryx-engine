#!/usr/bin/env python3
"""Run the ablation matrix and emit a JSON + Markdown report.

Light mode is CI-eligible (~3 min on devbox); heavy mode is on-demand and underlies the
Stage 4 pre-slice baseline. See PRD-0025 / ADR-0024.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from sematryx_engine.engine.ablation_benchmark import (
    AblationMatrixResult,
    CellResult,
    Verdict,
    default_heavy_seeds,
    default_light_seeds,
    default_scenarios,
    run_ablation_matrix,
)


def _cell_payload(cell: CellResult) -> dict[str, object]:
    return {
        "scenario": cell.scenario,
        "knob": cell.knob,
        "n_seeds": cell.n_seeds,
        "median_final_value": cell.median_final_value,
        "success_rate": cell.success_rate,
        "mean_evaluations": sum(cell.evaluations) / max(1, len(cell.evaluations)),
        "mean_wall_time_s": sum(cell.wall_times_s) / max(1, len(cell.wall_times_s)),
        "final_values": cell.final_values,
        "evaluations": cell.evaluations,
        "wall_times_s": cell.wall_times_s,
        "strategies": cell.strategies,
        "successes": cell.successes,
    }


def _result_to_json(
    result: AblationMatrixResult,
    *,
    generated_at: str,
    mode: str,
    git_rev: str | None,
) -> dict[str, object]:
    cells: dict[str, dict[str, object]] = {}
    for (scenario, knob), cell in result.cells.items():
        cells[f"{scenario}/{knob}"] = _cell_payload(cell)
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "mode": mode,
        "git_rev": git_rev,
        "matrix": {
            "scenarios": result.scenarios,
            "knobs": result.knobs,
            "seeds": result.seeds,
        },
        "cells": cells,
        "verdicts": [asdict(v) for v in result.verdicts],
    }


def _render_markdown(
    result: AblationMatrixResult,
    *,
    generated_at: str,
    mode: str,
    git_rev: str | None,
) -> str:
    lines = [
        "# Ablation matrix report",
        "",
        f"Generated: `{generated_at}`  ",
        f"Mode: `{mode}` (seeds N={len(result.seeds)})  ",
        f"Git rev: `{git_rev or 'unknown'}`",
        "",
        "Verdict rule (ADR-0024 §3): direction + significance only. "
        "`feature helps` = median worsens when off, p < 0.05. "
        "`regression` = median improves when off, p < 0.05. "
        "`no effect` = p ≥ 0.05.",
        "",
    ]
    verdicts_by_scenario: dict[str, list[Verdict]] = {}
    for v in result.verdicts:
        verdicts_by_scenario.setdefault(v.scenario, []).append(v)

    for scenario in result.scenarios:
        baseline_cell = result.cells[(scenario, "all_on")]
        lines.append(f"## `{scenario}`")
        lines.append("")
        lines.append(
            f"All-on baseline: median = `{baseline_cell.median_final_value:.6g}`  "
            f"success = `{baseline_cell.success_rate:.2f}`  "
            f"mean evals = `{sum(baseline_cell.evaluations) / max(1, len(baseline_cell.evaluations)):.1f}`"
        )
        lines.append("")
        lines.append(
            "| Knob off | Knob-off median | Δ median | p-value | Verdict |"
        )
        lines.append(
            "|----------|----------------|----------|---------|---------|"
        )
        for v in sorted(verdicts_by_scenario.get(scenario, []), key=lambda r: r.knob):
            lines.append(
                f"| `{v.knob}` "
                f"| `{v.knob_off_median:.6g}` "
                f"| `{v.delta_median_pct:+.2f}%` "
                f"| `{v.p_value:.3f}` "
                f"| **{v.verdict}** |"
            )
        lines.append("")

    return "\n".join(lines) + "\n"


def _git_rev() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip() or None
    except Exception:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("light", "heavy"),
        default="light",
        help="light (N=20 seeds, CI-eligible) or heavy (N=100, on-demand)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/process/verification/ablation"),
        help="Directory to write JSON + Markdown report",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="Filename label (default: ISO timestamp). Output filenames are "
             "ablation_<label>.json and ablation_<label>.md.",
    )
    args = parser.parse_args()

    seeds = default_light_seeds() if args.mode == "light" else default_heavy_seeds()
    scenarios = default_scenarios()

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    label = args.label or generated_at.replace(":", "").replace("-", "")
    git_rev = _git_rev()

    result = run_ablation_matrix(scenarios=scenarios, seeds=seeds)

    payload = _result_to_json(result, generated_at=generated_at, mode=args.mode, git_rev=git_rev)
    markdown = _render_markdown(result, generated_at=generated_at, mode=args.mode, git_rev=git_rev)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"ablation_{label}.json"
    md_path = args.output_dir / f"ablation_{label}.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
