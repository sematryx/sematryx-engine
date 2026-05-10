#!/usr/bin/env python3
"""Generate JSON + Markdown learning benchmark reports from domain scenarios."""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from sematryx_engine.engine.benchmark_metrics import collect_domain_benchmark_snapshot


def _render_markdown(payload: dict[str, object], generated_at: str) -> str:
    scenarios = payload.get("scenarios", {})
    lines = [
        "# Benchmark trend snapshot",
        "",
        f"Generated: `{generated_at}`",
        "",
        "| Scenario | Mode | Hit rate | Mean confidence | Runs | Target |",
        "|----------|------|----------|-----------------|------|--------|",
    ]
    if isinstance(scenarios, dict):
        for scenario_key in sorted(scenarios.keys()):
            block = scenarios.get(scenario_key, {})
            if not isinstance(block, dict):
                continue
            for mode in ("cold", "warm"):
                row = block.get(mode)
                if not isinstance(row, dict):
                    continue
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            str(row.get("domain", scenario_key)),
                            str(row.get("mode", mode)),
                            f"{float(row.get('hit_rate', 0)):.4f}",
                            f"{float(row.get('mean_confidence', 0)):.4f}",
                            str(row.get("runs", "")),
                            str(row.get("target_strategy") or "—"),
                        ]
                    )
                    + " |"
                )

    objectives = payload.get("objectives")
    if isinstance(objectives, dict) and objectives:
        lines.extend(
            [
                "",
                "## Objective quality",
                "",
                "| Scenario | Best value | Evaluations | Strategy | Dimensions |",
                "|-----------|------------|-------------|----------|------------|",
            ]
        )
        for key in sorted(objectives.keys()):
            row = objectives.get(key)
            if not isinstance(row, dict):
                continue
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row.get("scenario_name", key)),
                        f"{float(row.get('best_value', 0)):.6f}",
                        str(row.get("evaluations", "")),
                        str(row.get("strategy_used", "")),
                        str(row.get("dimensions", "")),
                    ]
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Cold rows reflect strategy selection without domain memory.",
            "- Warm rows reflect selection after repeated stored successes for the target strategy.",
            "- Objective rows include sphere benchmarks plus seeded discrete validation snapshots.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write JSON snapshot to this path (default: stdout only if no md-out)",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=None,
        help="Write Markdown summary to this path",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=100,
        help="Runs per cold/warm branch per scenario (default 100)",
    )
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        payload = collect_domain_benchmark_snapshot(
            tmp_path=Path(tmp),
            rugged_runs=args.runs,
            high_dim_runs=args.runs,
            discrete_selection_runs=args.runs,
        )
    payload_out = {
        "generated_at": generated_at,
        **payload,
    }

    json_text = json.dumps(payload_out, indent=2)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json_text + "\n", encoding="utf-8")
    else:
        print(json_text)

    if args.md_out is not None:
        md = _render_markdown(payload_out, generated_at)
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(md + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
