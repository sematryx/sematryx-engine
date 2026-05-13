# Integration Debt

## Current Deferred Items

- Continuous-path strategy recommendations remain domain-keyed only; richer bucketing on full
  `descriptor_learning_features` (beyond `descriptor_mix` on hybrid inner selection) is deferred.
- Hybrid **outer** loop (mixed variables in `sematryx_engine`): LCB acquisition + neighborhood
  refinement + staged budgets are integrated (ADR-0021, ADR-0023). **Full Bayesian / Gaussian-process /
  Thompson sampling** (or equivalent principled BO) over **discrete shells** in that outer loop
  remains **deferred** — optional dependencies, calibration, and heterogeneous inner SciPy noise (ADR-0023
  § Alternatives). Revisit when outer evaluations are the dominant cost and benchmarks justify it.
- Optional adapters for non-local backends (kept out of v1 core path).
- Expanded solver portfolio parity vs legacy project.
- Non-SciPy legacy continuous backends require optional package installation; calibration depth remains deferred.
- Full core-depth topology-to-solver integration and adaptive retry/tuning loop parity (runtime integrated; remaining debt is non-SciPy backends and broader parity benchmark matrix).
- Automated hyperparameter search grids / Bayesian tuning deferred beyond deterministic priors.
- Rich markdown/HTML explanation renderers are deferred; lightweight concise/verbose string helpers are now available.
- Longitudinal benchmark trend storage beyond generated snapshot files.
- Alternative reward transforms (e.g. log-scale) deferred pending analysis against objective snapshot metrics.
- **Ablation harness memory/bandit decoupling:** ADR-0025 ships a per-scenario warmup phase
  that populates `_MEMORY` and `_SELECTOR` before each measurement cell, so `memory_override`,
  `descriptor_mix_memory`, and `continuous_bandit` can all fire. Remaining deferred refinement:
  warmup updates *both* memory and the bandit in lockstep, so on scenarios where warmed memory
  and warmed bandit converge to the same strategy, those knobs read as `no effect` (a true
  finding under realistic warmup, not a measurement gap). A future refinement could
  decouple warmup writes — memory-only warmup, bandit-only warmup — to isolate each
  knob's unique contribution. Deferred until the question matters.
- **Subsystem port decisions surfaced by ADR-0027 substance audit.** The Engine vs
  Legacy-API Registry in `docs/process/ADOPTION_GATE.md` lists multiple subsystems
  in `decision needed` status (meta-learning, transfer learning, vector memory,
  knowledge graph, temporal intelligence, AI module). Each needs an explicit
  port/defer/drop decision before the next audit cycle. Likely outcomes for v1
  local-first scope: most → drop or defer; a few (bandit, explainability) may
  warrant partial port.
- **Stubs flagged for rename or implementation by ADR-0027 audit.** Bandit ("contextual"
  claim withdrawn — flat Thompson sampling), multi-attempt loop ("autodidactic" name
  overstated), decision metadata ("explanation" suggests reasoning, code is trace
  metadata), adaptation overlay ("tying" implies causality, code is static dict).
  Each needs a rename per ADR-0026 pattern or an actual implementation.
- **Periodic substance audit cadence.** ADR-0027 installed machine-checkable guards
  against new drift, but doesn't schedule re-audits to catch drift in subsystems
  not yet vocabulary-listed. Suggested cadence: every 10 PRs or quarterly.
  Currently informal — formalise after the post-ADR-0027 system runs for a quarter.

## Policy

Deferred items must be recorded here before being excluded from the current slice.

## Notes

- 2026-05-11: Continuous-path bandit exclusions for descriptor-only strategies are documented in ADR-0020 (defect guard, not a new deferred capability).
- 2026-05-11: Discrete benchmark trend rows and cold→warm acceptance evidence documented in ADR-0022 / PRD-0023.
