# Pre-Stage-4 ablation baseline — findings

**Source data:** `ablation_pre-stage-4.json` / `ablation_pre-stage-4.md`
**Methodology:** PRD-0025 / ADR-0024 (heavy matrix, N=100 seeds per cell, Mann-Whitney U with α=0.05).
**Git rev:** `bc5a1a5` (PR 2 head; current `main` plus PRs #32 #33).

## TL;DR

Across 4 scenarios × 8 ablation knobs × 100 seeds:

| Feature | Scenario | Δ when off | p | Verdict |
|---|---|---|---|---|
| `autodidactic_loop` | `rugged_multimodal_8d` | **+100.24%** | <0.001 | **feature helps** |
| `tuning_priors` | `rugged_multimodal_8d` | **+49.72%** | <0.001 | **feature helps** |
| `topology_routing` | *every scenario* | 0% | 1.000 | **override never fires** (see below) |
| (all other cells) | — | — | — | **no effect** (caveats below) |

Two features earn their complexity with statistically significant effects.
`topology_routing` reads as "no effect" — but follow-up analysis shows the override **never fires
on any tested scenario**, and the firing condition itself appears to have its budget term
inverted. The other "no effect" verdicts have documented methodology caveats.

## `topology_routing` — what the data actually says

The harness reports zero effect because flipping the `topology_routing` knob changes literally
nothing in the run. Strategy distributions are byte-identical across the on/off cells:

```
all_on (rugged_multimodal_8d):                  {'scipy_local_lbfgsb': 21, 'scipy_de': 79}
topology_routing=OFF (rugged_multimodal_8d):    {'scipy_local_lbfgsb': 21, 'scipy_de': 79}
```

The reason: the override's firing gate (`_topology_tunneling_override` in
[strategy_selector.py:35-48](src/sematryx_engine/engine/strategy_selector.py#L35-L48)) requires
`tunneling_directive == "aggressive"` or `physarum_tunneling_score >= 0.75`. None of our four
scenarios cross either threshold:

| Scenario | dims | budget/dim | regime | complexity | score | directive | fires? |
|---|---:|---:|---|---|---:|---|:---:|
| `sphere_smooth` | 4 | 50.0 | moderate | medium | 0.560 | balanced | ❌ |
| `rugged_multimodal_8d` | 8 | 50.0 | moderate | medium | 0.560 | balanced | ❌ |
| `discrete_knapsack` | 5 | 50.0 | moderate | medium | 0.560 | balanced | ❌ |
| `hybrid_mixed` | 5 | 64.0 | moderate | medium | 0.693 | balanced | ❌ |

**So the correct reading is "we have no data on whether topology routing helps, because the
gate never opens under any tested scenario,"** not "topology routing doesn't help."

### Suspected design defect: the budget term may be inverted

The score formula in [topology.py:64-71](src/sematryx_engine/engine/topology.py#L64-L71) is:

```
score = 0.45 * complexity_factor + 0.35 * budget_factor + 0.20 * span_variability
budget_factor: tight=1.0, moderate=0.7, generous=0.4
```

This routes "aggressive" tunneling (forces `scipy_dual_annealing`, a global optimizer) toward
**tight-budget** problems. The implicit reasoning is presumably "tight budget on a hard problem
is high-stakes, so make the most exploratory bet."

That reasoning is suspect. `scipy_dual_annealing` has explicit exploration (annealing) and
exploitation (local refinement) phases; both need budget. On a tight budget, dual_annealing can
exhaust evaluations exploring without converging — local methods with a reasonable start, or
single-restart `lbfgsb`/`powell`, extract more value per evaluation. The "excess budget →
afford exploration" framing reverses the budget term:

```
budget_factor (hypothesized fix): tight=0.4, moderate=0.7, generous=1.0
```

Same range, signs flipped. The complexity and span_variability terms stay as-is.

ADR-0006 documents the contract of the override but does not argue for the current budget
mapping; this is a heuristic that landed without a documented justification, and the data so
far does not support it.

## Implications for Stage 4 Slice 1

The original Slice 1 was "deepen Physarum tunneling beyond scaffolding." Based on this baseline,
the slice should be reshaped to **fix the heuristic, prove the fix, then deepen what works**:

1. **Add a scenario that triggers the override under the *current* (suspected-inverted) heuristic**
   — e.g. 13D rugged problem with `budget_per_dimension < 50`. Measure whether
   `scipy_dual_annealing` actually wins there. Predicted: it loses to `scipy_de` or even local
   methods because dual_annealing cannot converge in the given budget.
2. **Add a scenario that *would* trigger under the *inverted* heuristic** — e.g. moderate-to-high
   complexity with generous budget per dimension. Measure whether dual_annealing wins. Predicted:
   it wins.
3. If those predictions hold, **flip the `budget_factor` mapping** in `topology.py` (recorded as
   an ADR-0006 successor), re-run the baseline, and verify `topology_routing` now produces a
   real "feature helps" verdict on at least one scenario.
4. Only then deepen the topology integration (richer signals, more directives, etc.). Until
   step 3, every deepening change is optimizing against zero data.

`make ablation` is the regression gate for each step.

The `autodidactic_loop` and `tuning_priors` confirmations mean Slice 1 work that interacts with
those features can be measured against the current baseline immediately.

## Caveats on the other "no effect" verdicts

1. **`memory_override` / `descriptor_mix_memory`:** Each cell starts with an empty memory store
   (deliberate, to avoid cross-cell contamination from seed ordering). Memory override needs
   `usage_count >= 3` in domain to fire, so these knobs are measured by their fallback behaviour,
   not their effect on cold-start runs. Followup tracked in `INTEGRATION_DEBT.md`: add an
   optional per-scenario warmup phase.
2. **`hybrid_outer_acquisition` / `hybrid_outer_refinement`:** The `hybrid_mixed` scenario
   collapses to median=1 for every configuration — the discrete shell search consistently misses
   the optimum (disc=2, cat=1) by 1 given the budget. Scenario doesn't separate the hybrid path.
   Either grow the budget or redesign the objective to expose differences. Slice-2 scenario-design item.
3. **`continuous_bandit`:** With a cold bandit (0 prior reward updates), Thompson draws from
   `Beta(1, 1)` ≡ uniform random in expectation. The "no effect" here is structurally expected;
   measuring the bandit requires pre-training, which is the same warmup gap as the memory knobs.
4. **Single-machine, single-run baseline.** Effect sizes for the two "feature helps" verdicts
   are large enough that hardware drift is unlikely to flip those verdicts, but follow-up runs
   on different hardware are not yet collected.

## What this baseline becomes

- Reference point for every Stage 4 slice close: the per-feature, per-scenario medians and
  p-values are the "before" data any future slice must beat for the features it touches.
- Source of the Slice 1 scope reshape recorded above.
- Input to the next methodology iteration (warmup-phase scenarios for memory- and
  bandit-dependent knobs).

## Next steps

- Land PRs #32 and #33 first, then this PR.
- Open Slice 1 with the reshape above: heuristic fix first, deepening after.
- Track warmup-phase methodology refinement as a sibling slice (or absorb into Slice 1 if it
  blocks topology measurement on hybrid/memory cases).
