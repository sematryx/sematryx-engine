# Pre-Stage-4 ablation baseline — findings

**Source data:** `ablation_pre-stage-4.json` / `ablation_pre-stage-4.md`
**Methodology:** PRD-0025 / ADR-0024 (heavy matrix, N=100 seeds per cell, Mann-Whitney U with α=0.05).
**Git rev:** `bc5a1a5` (PR 2 head; current `main` plus PRs #32 #33).

## TL;DR

Across 4 scenarios × 8 ablation knobs × 100 seeds, only **two features earn their complexity** with statistically significant effects:

| Feature | Scenario | Δ median when off | p | Verdict |
|---|---|---|---|---|
| `autodidactic_loop` | `rugged_multimodal_8d` | **+100.24%** | <0.001 | **feature helps** |
| `tuning_priors` | `rugged_multimodal_8d` | **+49.72%** | <0.001 | **feature helps** |

**All other (feature × scenario) cells read `no effect`.** Most notably:

- **`topology_routing` shows zero effect on every scenario**, including the topology-sensitive `rugged_multimodal_8d`. The Physarum tunneling override does not change outcomes under the current scenario suite.
- `hybrid_outer_acquisition` and `hybrid_outer_refinement` show no effect, but `hybrid_mixed` converges to a flat median=1 floor for every configuration, so the scenario is not separating the hybrid path.
- `memory_override` and `descriptor_mix_memory` show no effect; this is the documented cold-state-per-cell methodology caveat (`INTEGRATION_DEBT.md`) — they require `usage_count ≥ 3` in domain, which cannot occur with fresh per-cell singletons.
- `continuous_bandit` shows no effect even on the rugged scenario; the bandit's per-cell cold start may not have enough updates to differ from uniform random.

## Implications for Stage 4 Slice 1

The proposed Slice 1 was "**deepen Physarum tunneling + routing evidence beyond scaffolding**" — built on the implicit assumption that the existing topology integration earns its complexity. This baseline says it does not, at least not under the current scenarios.

**Recommended reshape of Slice 1:**

1. **Before deepening**, build at least one scenario where `topology_routing=False` produces a measurably worse result than the all-on baseline. If no such scenario can be constructed, the topology→routing wiring is not delivering value and Slice 1 should reconsider the design (not just deepen it).
2. Once such a scenario exists, treat it as the regression gate for any topology change in Slice 1. Use `make ablation` to verify each step.
3. The `autodidactic_loop` and `tuning_priors` confirmations mean Slice 1 work that interacts with those features can be measured against the baseline immediately.

This is the validate-before-build outcome we wanted from PRD-0025: a concrete signal that part of Slice 1's premise needs adjustment **before** any code lands.

## Caveats and known methodology gaps

1. **Memory features cannot fire** under cold-state-per-cell isolation (`INTEGRATION_DEBT.md` entry). `memory_override` and `descriptor_mix_memory` are not measured on their effect; they are measured on their fallback behaviour. A warmup-phase scenario extension is the documented followup.
2. **`hybrid_mixed` does not separate the hybrid path.** Median collapses to 1 for every configuration — likely the discrete shell search misses the optimum (disc=2, cat=1) by 1 with high consistency given the budget. Either the budget needs to grow or the objective needs to be redesigned to expose differences in `hybrid_outer_acquisition` / `hybrid_outer_refinement`. Track as a Slice-2 scenario-design item.
3. **`continuous_bandit=False` is uniform random over candidates.** On cold cells the bandit has 0 prior reward updates, so its Thompson draw is from `Beta(1, 1)` — equivalent to uniform random in expectation. The "no effect" verdict for this knob is therefore expected; the bandit only differs from uniform once it has reward history. To measure it properly, scenarios need a warmup phase that pre-trains the bandit (related to the memory-warmup gap).
4. **Single-machine, single-run baseline.** The verdicts here are valid for the configurations we ran; a second baseline on different hardware could shift confidence intervals slightly. Effect sizes for the two "feature helps" verdicts are large enough that hardware drift is unlikely to flip those verdicts.

## What this baseline becomes

- Reference point for every Stage 4 slice close: the per-feature, per-scenario medians and p-values are the "before" data any future slice must beat (for the features it touches).
- Source of the Slice 1 scope adjustment recommended above.
- Input to the next methodology iteration (warmup-phase scenarios for memory- and bandit-dependent knobs).

## Next steps

- Land PRs #32 and #33 first, then this PR.
- Open a follow-up that reshapes Slice 1 scope: scenario design first, deepening second.
- Track warmup-phase methodology refinement as a sibling slice (or absorb into Slice 1 if it blocks topology measurement).
