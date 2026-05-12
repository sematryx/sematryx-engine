# PRD-0025: Stage 4 Ablation Harness

## Problem Statement

Stage 2/3 integrated topology routing, tuning priors, autodidactic attempts, memory override,
and descriptor-mix memory without isolated A/B evidence that each feature improves outcomes.
Stage 4 acceptance criteria 2 and 5 require *measurable* effect of topology signals and the
multi-attempt loop. Without an ablation harness we cannot close those criteria and risk
deepening features that do not earn their complexity in Slice 1 onward.

## Goals

- Make each integrated feature independently toggleable to a documented neutral fallback.
- Run a fixed scenario × ablation matrix with deterministic seeds and emit a structured report
  (JSON + Markdown) usable for every Stage 4 slice.
- Establish a one-time **pre-Stage-4 baseline** measurement of `main` so later slices have a
  shared reference.
- Production callers retain byte-identical behaviour when no ablation is supplied.

## Non-Goals

- Adding new optimization features or scenarios beyond what is needed to separate signals.
- Replacing or rewriting `benchmark_metrics.py` / trend reporting; extend, do not duplicate.
- Making any ablation result a CI merge gate in this PRD (the gate decision is a follow-up).
- New optional dependencies. SciPy + stdlib only.

## Functional Requirements

1. **`AblationConfig`** (frozen dataclass) with independent boolean knobs covering all
   integrated optimizer features, not just Stage 4 scaffolds:
   - `topology_routing` (Stage 4 — physarum tunneling override)
   - `tuning_priors` (Stage 4 — `compute_solver_tuning_priors` output)
   - `autodidactic_loop` (Stage 4 — multi-attempt budget split)
   - `memory_override` (Stage 2 — warm-history selection override)
   - `descriptor_mix_memory` (Stage 3 / ADR-0023 — JSON1-filtered memory rankings)
   - `hybrid_outer_acquisition` (Stage 3 / ADR-0023 — LCB shell scoring)
   - `hybrid_outer_refinement` (Stage 3 / ADR-0021 — neighborhood refinement loop)
   - `continuous_bandit` (Stage 2 — UCB-style strategy selection)

   `AblationConfig.default()` is all-on and is the only path production code follows when
   no config is passed.
2. **`optimize(...)`** accepts an optional `ablation: AblationConfig | None = None`. When
   `None` or `AblationConfig.default()`, output must be byte-identical to the pre-PRD
   behaviour for a fixed seed (covered by an identity test).
3. **Neutral fallbacks** (documented in ADR-0024) for each off-knob: skip the
   `physarum_tunneling_override`, return a neutral tuning-priors dict, force
   `attempt_limit = 1`, bypass the memory override, and pass `memory_descriptor_mix=None`
   respectively. Each fallback is deterministic.
4. **`run_ablation_matrix(scenarios, knobs, seeds)`** in `engine/ablation_benchmark.py`
   returns per-cell metrics (median final value, success rate, evaluations-to-target,
   wall-time) and per-knob deltas vs the all-on baseline, with Mann-Whitney U p-values on
   final values across seeds.
5. **Report generator** `scripts/generate_ablation_report.py` emits JSON + Markdown with a
   verdict column per (scenario, knob) per the rule in ADR-0024.
6. **Makefile** `make ablation` (light: 4 scenarios × 8 knobs × 20 seeds, target <3 min) and
   `make ablation-full` (heavy: 100 seeds, on-demand).
7. **Pre-Stage-4 baseline** committed under `docs/process/verification/baselines/` as the
   reference point for all Stage 4 slices.

## Acceptance Criteria (Checklist)

- [ ] `AblationConfig` dataclass exists with the eight knobs above and a `default()` classmethod.
- [ ] `optimize(...)` accepts `ablation` kwarg without altering default-path results
      (byte-identity test on at least 3 scenarios × 3 seeds).
- [ ] Each neutral fallback has a unit test that proves the off-path is deterministic and
      independent of the integrated path.
- [ ] `run_ablation_matrix` returns a structured result usable by the report generator and
      runs the light matrix in under 2 minutes on devbox.
- [ ] `scripts/generate_ablation_report.py` produces a JSON + Markdown report with the
      verdict column populated per ADR-0024 rule.
- [ ] `make ablation` and `make ablation-full` exist and are documented in `DEVELOPMENT_WORKFLOW.md`.
- [ ] Pre-Stage-4 baseline report is committed; `ACTIVE_PLAN` Stage 4 preview notes the baseline.
- [ ] ADR-0024 records the ablation boundary, fallback semantics, and verdict thresholds.
- [ ] VR-0025 documents byte-identity evidence, light-matrix runtime, and a snapshot of the
      baseline verdict table.

## Execution Plan

- [ ] **PR 1** — `engine/ablation.py` (config + fallbacks), `optimize(...)` wiring at every
      affected call site (selector override, priors, attempt budget, memory override,
      descriptor_mix filter, hybrid LCB/refinement, bandit selection), unit tests for each
      fallback, byte-identity integration test.
- [ ] **PR 2** — `engine/ablation_benchmark.py` (`run_ablation_matrix`), the verdict logic,
      `scripts/generate_ablation_report.py`, `make ablation` / `make ablation-full`, light
      integration test (smaller matrix) under `tests/performance/`.
- [ ] **PR 3** — One-time heavy baseline run, commit the report + a short findings doc, link
      from `ACTIVE_PLAN`. No production code changes.

## Risks

- **Bypass complexity in `optimizer.py`**: branching on eight knobs at multiple call sites
  risks accidental divergence between on/off paths. Mitigation: all branching reads through
  a single `AblationConfig` instance; byte-identity test guards the default path; each
  off-path is the documented pre-feature historical behaviour, so it has prior art to
  verify against.
- **Noise in light matrix**: 20 seeds may not separate small effects. Mitigation: report
  p-values; verdict thresholds (ADR-0024) require both effect size and significance.
- **Devbox runtime drift**: heavy matrix may exceed 15 min on slower hardware. Mitigation:
  heavy run is on-demand only; runtime is part of VR-0025 evidence, not a CI gate.

## Rollout Plan

PRs 1 → 2 → 3 land **strictly sequentially**. Stage 4 Slice 1 does not start until PR 3
lands. Rationale: Slice 1 (deepen Physarum tunneling + routing) is built on the assumption
that the existing topology integration earns its complexity; if PR 3 verdicts that
assumption away, Slice 1's premise changes shape. Parallel work risks rebuilding Slice 1
from a different premise for one session of speed gain.

Light `make ablation` is informational once PR 2 lands; not a merge gate. PR 3 freezes the
baseline report in `docs/process/verification/baselines/`.

## Verification Link

`docs/process/verification/VR-0025-stage4-ablation-harness.md`
