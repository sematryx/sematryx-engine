# Pre-Stage-4 ablation baseline — findings

> **Note on terminology (2026-05-13, ADR-0026):** The baseline JSON/Markdown artefacts
> below were produced *before* the topology→shape rename. They use the old field names
> (`topology_routing`, `physarum_tunneling_score`, `tunneling_directive`,
> `topology_firing_current`). In current code these are `shape_routing`,
> `shape_routing_score`, `shape_routing_directive`, `shape_routing_firing_current`.
> The verdicts in this doc are valid but **narrower than their original framing**:
> "topology_routing helps" should be read as "**shape_routing helps**" — the override
> measured here gates strategy choice on problem-space shape (dimensions, budget,
> bound widths), not on any objective-landscape topology. The real topology pipeline
> (Physarum mapping + topology-informed tunneling) is Stage 4 Slice 1; baselines after
> that ships will use the corrected names.

**Current baseline (v2):** `ablation_pre-stage-4-v2.json` / `ablation_pre-stage-4-v2.md`
**Historical (v1, no warmup, 4 scenarios):** `ablation_pre-stage-4.json` / `ablation_pre-stage-4.md`
**Methodology:** PRD-0025 / ADR-0024 (verdict rule) + ADR-0025 (warmup + firing scenarios).
**Heavy matrix:** N=100 seeds × 6 scenarios × 8 knobs, Mann-Whitney U with α=0.05.
**Git rev (v2):** `1ecbcec` (pre-rename).

## TL;DR

The v2 baseline closes the "untested features" gap. Every knob now has a real verdict against
at least one scenario where it can fire:

| Feature | Best scenario | Δ when off | p | Verdict |
|---|---|---|---|---|
| `topology_routing` | `topology_firing_current` | **+71.19%** | <0.001 | **feature helps** |
| `autodidactic_loop` | `rugged_multimodal_8d` | +48.11% | <0.001 | **feature helps** |
| `tuning_priors` | `rugged_multimodal_8d` | +48.11% | <0.001 | **feature helps** |
| `hybrid_outer_refinement` | `hybrid_separating` | (essential, see below) | <0.001 | **feature helps** |
| `memory_override` | `rugged_multimodal_8d` (warmed) | 0% median, distributional | <0.001 | rank shift only |
| `continuous_bandit` | (none) | 0% | ≥0.473 | **no effect** |
| `descriptor_mix_memory` | (none) | 0% | 1.000 | **no effect** |
| `hybrid_outer_acquisition` | (none) | 0% | ≥0.577 | **no effect** |

**Four features confirmed helpful** (with statistically significant median shifts). **One**
(`memory_override`) shifts the distribution without moving the median — a true secondary finding.
**Three** (`continuous_bandit`, `descriptor_mix_memory`, `hybrid_outer_acquisition`) show no
detectable effect even when their firing conditions are present.

## Headline reversal vs v1: topology routing helps, not hurts

The v1 findings doc recorded that `topology_routing` showed zero effect across all scenarios and
hypothesised that the underlying `budget_factor` heuristic was sign-inverted (tight budgets
should not trigger aggressive global search). **The v2 firing-scenario data refutes that
hypothesis on the scenario tested:**

```
topology_firing_current (13D rugged, budget=600, budget/dim=46.15 → tight regime):
  all_on (override fires):           100/100 picks scipy_dual_annealing  → median 0.951
  topology_routing=OFF (bandit):     33 dual_annealing, 38 shgo, 29 de   → median 1.628
                                                                            Δ +71%, p<0.001
```

`scipy_dual_annealing` (forced by the override) beats the bandit's natural mix on 13D tight-budget
rugged problems. The current `budget_factor: tight=1.0` mapping appears correct on at least this
scenario.

**Slice 1 reshape:** the heuristic-flip task is withdrawn. Slice 1 instead **expands topology
coverage** — adds firing scenarios at other (`complexity`, `budget_regime`) combinations and
measures whether the override helps, hurts, or is no-op on each. The space of (dimensions ×
budget × landscape) is large; v2 only tests one firing point.

## Per-feature interpretation

### `topology_routing` — confirmed helper on tested firing scenario

Strategy distributions show the override pinning every seed to `scipy_dual_annealing`, vs the
bandit splitting picks across three globals when free. The forced pick wins by 71%. Worth noting:
the bandit picks `scipy_dual_annealing` itself on 33/100 free seeds, so the override only changes
the routing on 67/100 cells — the magnitude implies dual_annealing is meaningfully better than
shgo/de on this specific landscape.

### `autodidactic_loop` and `tuning_priors` — confirmed helpers

Δ dropped from +100% (v1) to +48% (v2) because warmup populates the bandit with high-quality
priors, narrowing the gap that autodidactic and priors close. The verdict is unchanged.

### `hybrid_outer_refinement` — essential on hybrid_separating

Baseline median = `2.46e-32` (numerical zero — the refinement loop reliably finds the optimum).
With refinement disabled, median = `4` (consistently misses the optimum by one discrete step in
multiple dims). The reported Δ% is an artefact of dividing by a near-zero baseline; the meaningful
statement is **"the hybrid solver does not find the optimum without the refinement loop."**

### `memory_override` — distributional shift without median shift

Same medians (`0.4713`) on both on/off, but Mann-Whitney p<0.001. The strategy distributions
explain it:
- On: 62 scipy_de + 38 scipy_local_lbfgsb
- Off: 88 scipy_de + 12 scipy_local_lbfgsb

Both `scipy_de` and `scipy_local_lbfgsb` happen to reach the same value on the rugged
multimodal landscape from warm starts, so the median doesn't move; but the override's deterministic
pick of `scipy_de` shifts which seeds land at what value. The verdict reads `no effect` because the
rule keys off median direction; the rank-test signal is real but not actionable here.

Followup: the verdict rule could grow a fourth category (`distributional only` or similar) for
features that shift ranks without medians. Deferred — adding categories now without more examples
risks overfitting the rule to one finding.

### `continuous_bandit` — no detectable effect under warmup

Even with the bandit warmed for 10 runs, uniform random over the candidate filter produces
indistinguishable outcomes. Implication: the candidate filter (by complexity / dimensions in
`strategy_selector.py:90-96`) is doing most of the work; the bandit's relative ranking among the
remaining candidates barely matters on the tested scenarios.

Followup: try a scenario where the filter returns a larger candidate set (low-dimensional
mixed-complexity problems), so the bandit has more arms to discriminate.

### `descriptor_mix_memory` and `hybrid_outer_acquisition` — no effect on tested scenarios

The descriptor_mix filter requires mixed-history memory rows; warmup populates them but the
resulting recommendations don't differ from domain-only rankings in any way that changes the
hybrid inner solver's pick. LCB acquisition exploration likewise doesn't separate from uniform
shell sampling — the **refinement** loop is doing the heavy lifting in the hybrid path.

Followup: a hybrid scenario where the *exploration* phase matters (very tight inner budgets,
forcing the outer to commit early) might separate LCB from random. Deferred.

## What changed from v1 to v2

- **Knobs measurable**: 2 → 5 (3 more given real signal; 3 still "no effect" but now under
  conditions where they could fire).
- **Scenarios**: 4 → 6 (`topology_firing_current` and `hybrid_separating` added; `hybrid_mixed`
  retained as legacy reference).
- **Methodology**: cold-state-per-cell → per-(scenario, seed) warmup snapshots cached across knob
  cells (ADR-0025).
- **Runtime**: heavy matrix ~5 min → ~15 min.
- **Major hypothesis reversal**: the budget-factor-inversion hypothesis from v1's findings is
  **withdrawn**. The current heuristic correctly routes on the tested firing scenario.

## Implications for Stage 4 Slice 1

The original Slice 1 ("deepen Physarum tunneling beyond scaffolding") and the v1 reshape
("scenario design before flipping the heuristic") both need adjustment. The v2 data supports:

1. **The current topology heuristic is not wrong on every firing scenario.** It works on the
   single firing point we tested. Before deepening or modifying it, **measure more firing points**
   — different (complexity, budget) combinations, different landscape types — and see whether the
   verdict generalises.
2. **`hybrid_outer_refinement` is load-bearing.** Slice 1 should not casually change this — it's
   the difference between finding the optimum and missing by 4 on `hybrid_separating`.
3. **`hybrid_outer_acquisition` (LCB exploration) is dispensable on tested scenarios.** Worth
   measuring whether it has a regime where it matters; if not, it could be simplified or removed.
4. **`memory_override`'s distributional effect** deserves a separate scenario where memory and
   bandit pick genuinely different strategies (synthetic warm-up). That's a methodology slice
   sibling to topology coverage.

## Caveats

1. **Single-machine, single-run baseline.** Effect sizes are large enough that hardware drift is
   unlikely to flip the four "feature helps" verdicts, but follow-up runs on different hardware
   are not yet collected.
2. **Δ% near zero baselines is misleading.** The `hybrid_outer_refinement` row shows a
   nonsensical large percentage because the baseline median is ~1e-32; the real statement is
   "feature is essential." A future report-generator change could replace Δ% with absolute Δ when
   the baseline is below a configurable threshold.
3. **"No effect" verdicts apply to the tested scenarios only.** Three knobs still need more
   targeted scenarios before we can confidently say they don't add value in general.
4. **Discrete and `hybrid_mixed` scenarios floor at the optimum/floor for every config.** They
   contribute no separation signal and could be retired from the default suite — kept for now
   as legacy reference.
