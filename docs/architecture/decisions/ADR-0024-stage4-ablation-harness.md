# ADR-0024: Stage 4 Ablation Harness — Configuration Boundary and Verdict Methodology

## Status

Accepted

## Context

Stage 4 acceptance criteria require measurable effect of topology routing (criterion 2) and
the multi-attempt adaptive loop (criterion 5). The integrated `optimize(...)` path mixes
topology routing, tuning priors, autodidactic attempts, memory override, and descriptor-mix
memory; structural tests show each component runs but do not isolate its contribution. We
need a way to A/B each feature against a documented neutral fallback without polluting the
production call path or adding new optional dependencies.

## Decision

1. **Single configuration boundary.** A frozen `AblationConfig` dataclass with one boolean
   per integrated feature, covering all stages — not just Stage 4 scaffolds — so that
   Stage 2/3 features that confound Stage 4 measurements can be ablated independently:
   `topology_routing`, `tuning_priors`, `autodidactic_loop`, `memory_override`,
   `descriptor_mix_memory`, `hybrid_outer_acquisition`, `hybrid_outer_refinement`,
   `continuous_bandit`. `AblationConfig.default()` is all-on. `optimize(...)` accepts
   `ablation: AblationConfig | None = None`; when `None`, the call path is byte-identical
   to the pre-PRD behaviour (enforced by integration test).

2. **Neutral fallbacks (deterministic, documented).** Each off-path is the pre-feature
   historical behaviour, so prior commits/tests serve as verification anchors:
   - `topology_routing=False`: `_topology_tunneling_override` returns `None`; routing falls
     back to bandit + memory only. Topology artifact is still built and reported.
   - `tuning_priors=False`: `compute_solver_tuning_priors(...)` returns a frozen "neutral"
     dict — `budget_multiplier=1.0`, `de_polish=True`, `de_population_scale=1.0`,
     `dual_annealing_restart_temp_ratio=2e-5` (the existing tight-regime default),
     `shgo_sampling_scale=1.0`, `version=1`.
   - `autodidactic_loop=False`: `attempt_limit` forced to `1`, full `max_evaluations` to
     the single attempt. `attempts` list still recorded for explanation parity.
   - `memory_override=False`: `select_with_basis` skips memory override; bandit + topology
     override only.
   - `descriptor_mix_memory=False`: hybrid inner passes `memory_descriptor_mix=None`;
     domain-only ranking applies (pre-ADR-0023 behaviour).
   - `hybrid_outer_acquisition=False`: hybrid outer falls back to uniform shell sampling
     without LCB scoring (pre-ADR-0023 behaviour).
   - `hybrid_outer_refinement=False`: hybrid outer runs a single exploration pass without
     the neighborhood refinement loop (pre-ADR-0021 behaviour).
   - `continuous_bandit=False`: strategy selector returns a uniform random pick over
     eligible strategies (seeded via the same RNG as the rest of the run). Memory and
     topology overrides, when enabled, still apply on top of the random base.

3. **Verdict rule (per scenario × knob).** Direction + significance only — no arbitrary
   effect-size thresholds. Magnitude is reported alongside the verdict so any "helps"
   verdict is qualified by how much it helps (0.3% vs 30% are very different signals even
   if both are significant):
   - Run N seeds with the knob off; compute Mann-Whitney U p-value on final values vs the
     all-on baseline at the same seeds.
   - **"feature helps"** if median worsens when off (Δ > 0) with p < 0.05.
   - **"no effect"** if p ≥ 0.05.
   - **"regression"** if median improves when off (Δ < 0) with p < 0.05 (feature is
     actively hurting on this scenario).

   Every report row carries `Δ_median_pct`, `p_value`, and `verdict`. Effect-size thresholds
   were considered (5% / 2%) but rejected as arbitrary; let the magnitude column speak. A
   "feature helps" verdict with Δ = 0.3% is still a signal worth reporting, just a small
   one — readers can weigh it against the cost of the feature.

4. **Test methodology:**
   - Mann-Whitney U (non-parametric, scale-free, no normality assumption).
   - Common seeds across on/off cells per scenario (paired comparison).
   - Light matrix N=20, heavy matrix N=100. Light is CI-eligible (informational); heavy is
     on-demand for baseline + slice-close evidence.

5. **No new dependencies.** Mann-Whitney U is implemented via `scipy.stats.mannwhitneyu`
   (already a hard dependency). No `numpy.random` calls outside seeded `random.Random`.

## Alternatives Considered

- **Environment variable flags** (e.g. `SEMATRYX_ABLATE_TOPOLOGY=1`): rejected. Implicit
  state, hard to test, easy to leak between runs.
- **Separate `ablated_optimize(...)` function**: rejected. Duplicates the entire optimizer
  body and guarantees on/off divergence over time.
- **Parametric `pytest.mark.parametrize` over scenarios only**: rejected. Couples test
  harness to scenario list; no reusable runner for Stage 4 slice closes.
- **Bootstrap confidence intervals instead of Mann-Whitney**: viable but more code; defer
  unless verdict rule turns out to be too coarse.

## Consequences

- **Positive:** every Stage 4 feature can be measured against a documented neutral fallback
  without changing production callers; the baseline doc becomes the reference point for
  Slice 1 onward; criteria 2 and 5 have a concrete evidence path.
- **Negative:** branching on eight knobs across selector, priors, attempt loop, memory,
  hybrid outer, and bandit call sites adds surface area; mitigated by routing all checks
  through a single `AblationConfig` instance, a byte-identity test on the default path, and
  the fact that every off-path is a historical pre-feature behaviour with prior art.
- **Follow-up tasks:**
  - VR-0025 includes byte-identity proof and light-matrix runtime.
  - Stage 4 Slice 1 close uses the harness; if verdict is "no effect" or "regression" on
    the existing topology integration, Slice 1 scope expands to address that first.
  - Decide post-baseline whether to promote `make ablation` to a CI merge gate.
