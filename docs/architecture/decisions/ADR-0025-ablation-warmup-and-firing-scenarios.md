# ADR-0025: Ablation Harness — Warmup Methodology + Firing Scenarios

## Status

Accepted

## Context

The pre-Stage-4 baseline (`docs/process/verification/baselines/ablation_pre-stage-4.md`,
ADR-0024) produced verdicts for only 2 of the 8 ablation knobs. The other 6 read as `no
effect` for two distinct reasons that the harness, as designed in ADR-0024, could not
resolve:

1. **Methodology gap — cold-state-per-cell.** Each cell starts with empty `_MEMORY` and
   `_SELECTOR`, so `memory_override` cannot fire (needs `usage_count >= 3`) and
   `continuous_bandit` operates on `Beta(1, 1)` priors (≈ uniform random in expectation).
   `descriptor_mix_memory` is shadowed by the same gap.
2. **Scenario gap — gate never opens / floor convergence.** No tested scenario crosses the
   `physarum_tunneling_score >= 0.75` threshold, so `topology_routing` never fires.
   `hybrid_mixed` converges to median=1 for every configuration, so `hybrid_outer_acquisition`
   and `hybrid_outer_refinement` have no separation to detect.

The project's standing principle is **no untested features before moving forward**. This
ADR records the methodology changes required to give every knob a real verdict in the next
baseline.

## Decision

### 1. Per-scenario warmup phase

Extend `AblationScenario` with `warmup_runs: int = 0` (defaulting to current cold-cell
behaviour). When `warmup_runs > 0`, the runner executes that many `optimize(...)` calls
with `AblationConfig.default()` *before* the measurement run, against the same singleton
isolation root. This populates `_MEMORY` (via `store_optimization_result`) and
`_SELECTOR._bandit` (via `update`) so history-dependent knobs can fire.

### 2. Cached snapshot per `(scenario, seed)`

A single warmup pass per `(scenario, seed)` populates a snapshot directory containing
`strategy_memory.db` and `bandit_state.json`. Every knob cell for that scenario × seed
copies the snapshot into a fresh per-cell isolation root before running the measurement.
This keeps cells independent (so seed ordering and knob ordering still cannot contaminate
each other) while reusing warmup work across the 9 knob cells (baseline + 8 knobs).

Cost estimate: with 3 warmed scenarios at `warmup_runs=10`, 100 seeds, and 6 scenarios total,
the warmup adds ~3000 cached runs to the heavy matrix vs the ~27000 runs it would cost
without caching. Net heavy-matrix runtime grows from ~5 min (baseline v1) to ~15 min on devbox.

### 3. Warmup seeds derived deterministically

Warmup run *w* under measurement seed *s* uses RNG seed `s * 1000 + w`. This is
deterministic per (seed, w) and disjoint from the measurement seed space (which uses
1001–1100), so warmup never collides with measurement seeds.

### 4. New scenarios

- **`topology_firing_current`** — 13D rugged, `max_evaluations=600`. By construction:
  `budget_per_dimension = 46.15 < 50` → `tight` regime → `budget_factor=1.0`; `dimensions >
  12` → `complexity_hint="high"` → `complexity_factor=1.0`; uniform bounds →
  `span_variability=0`. Score = `0.45·1.0 + 0.35·1.0 + 0.20·0 = 0.80` → directive =
  `aggressive` → topology override **fires** and forces `scipy_dual_annealing`.
  `warmup_runs=0` so the topology path is the dominant routing signal (warmed memory would
  fire ahead of topology in `select_with_basis` order).

- **`hybrid_separating`** — 4 integer dimensions ∈ [0,5] (6⁴ = 1296 discrete shells) × 2
  continuous, `max_evaluations=600`. Outer exploration visits ~20 shells out of 1296; LCB
  acquisition should concentrate visits near improving shells, uniform random should not.
  Smooth quadratic discrete cost gives LCB-vs-uniform a gradient to work with (vs
  `hybrid_mixed`'s step-function floor).

Scenario B (13D generous-budget, would fire only after the proposed `budget_factor` sign
flip) is **deferred** to whichever PR ships the sign flip — adding it now leaves a scenario
that produces no signal under current code, violating the "no untested" principle.

### 5. Per-scenario warmup configuration

| Scenario | `warmup_runs` | Why |
|---|---:|---|
| `sphere_smooth` | 0 | Trivial problem; strategy choice doesn't matter; warmup adds cost without separation |
| `rugged_multimodal_8d` | 10 | Memory + bandit warmup so `memory_override` and `continuous_bandit` can fire |
| `discrete_knapsack` | 10 | Same |
| `hybrid_separating` | 10 | Mixed descriptors so `descriptor_mix_memory` can fire |
| `topology_firing_current` | 0 | Topology override must fire ahead of any warmed memory override |

`warmup_runs = 10` was chosen empirically: Thompson-sampling exploration scatters picks
across ~5 strategies in the first 5 warmup runs, leaving every strategy at
`usage_count = 1` and the override gate (`usage_count >= 3`) closed. By 10 runs the
bandit's posterior concentrates enough that the dominant strategy clears the threshold
on ≥60% of seeds. Lower values trade for runtime but leave a methodology gap; higher
values are wasted budget. An integration test under `tests/performance/` enforces the
60% firing rate so this can't silently regress.

`hybrid_mixed` is retained in the suite for now (existing baseline reference) but flagged
as a known floor-convergence scenario in the findings doc.

### 6. Selector firing-order interaction

The existing `select_with_basis` order is: memory_override → topology_routing → bandit.
After warmup, memory_override fires on any scenario with `warmup_runs > 0`, so
topology_routing on those scenarios is shadowed. This is *intentional* — the
`topology_firing_current` scenario keeps `warmup_runs=0` precisely so topology can be
measured without the memory shadow. Each knob has at least one scenario where it can
plausibly fire independently of the others.

## Alternatives Considered

- **Per-cell warmup, no caching.** Simpler code but ~3× more wall-time on the heavy run
  (~20 min instead of ~9). Rejected — caching is a small amount of code for a meaningful
  runtime improvement.
- **Warmup with deliberately suboptimal strategies** (to force memory_override to differ
  from the bandit's pick). Rejected as a default — too synthetic. The harness measures the
  override mechanism under realistic conditions; if memory + bandit agree post-warmup, the
  "no effect" verdict is a true finding, not a methodology gap.
- **Decouple memory writes from bandit writes during warmup.** Considered for cleaner
  isolation of `memory_override` vs `continuous_bandit`. Rejected for v1 — it requires
  reaching past the production API and the data on whether it's needed isn't in yet.
- **Add Scenario B (generous-budget topology firing) now.** Rejected per the user's "no
  untested" principle; it doesn't fire under current code and would be a placeholder.

## Consequences

- **Positive:** Every knob has a scenario where it can fire; the next heavy baseline
  produces a verdict for all 8. The "memory warmup" row in `INTEGRATION_DEBT.md` is closed
  (or reduced to "memory-vs-bandit decoupling deferred").
- **Negative:** Heavy matrix runtime grows from ~5 min to ~9 min; one new firing scenario
  adds ~13D × 600 evals of `scipy_dual_annealing` per cell that fires. Light matrix grows
  from ~30s to ~75s.
- **Follow-up tasks:**
  - VR (verification report) for PR 4 includes the new baseline `v2` snapshot and a table
    showing every knob now has a verdict.
  - If the post-warmup baseline still shows `memory_override` and `continuous_bandit` as
    "no effect" because warm bandit + warm memory agree, document that as the *true*
    finding rather than a measurement gap.
  - Sign flip on `budget_factor` (ADR-0006 successor) becomes the next slice once
    Scenario A's data confirms the inversion hypothesis.
