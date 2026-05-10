# Integration Debt

## Current Deferred Items

- Continuous-path strategy recommendations remain domain-keyed only; richer bucketing on full
  `descriptor_learning_features` (beyond `descriptor_mix` on hybrid inner selection) is deferred.
- Hybrid **outer** loop: LCB acquisition + neighborhood refinement + staged budgets are integrated
  (ADR-0021, ADR-0023). Full GP / Thompson outer surrogates remain deferred.
- Optional adapters for non-local backends (kept out of v1 core path).
- Expanded solver portfolio parity vs legacy project.
- Non-SciPy legacy continuous backends require optional package installation; calibration depth remains deferred.
- Full core-depth topology-to-solver integration and adaptive retry/tuning loop parity (runtime integrated; remaining debt is non-SciPy backends and broader parity benchmark matrix).
- Automated hyperparameter search grids / Bayesian tuning deferred beyond deterministic priors.
- Rich markdown/HTML explanation renderers are deferred; lightweight concise/verbose string helpers are now available.
- Longitudinal benchmark trend storage beyond generated snapshot files.
- Alternative reward transforms (e.g. log-scale) deferred pending analysis against objective snapshot metrics.

## Policy

Deferred items must be recorded here before being excluded from the current slice.

## Notes

- 2026-05-11: Continuous-path bandit exclusions for descriptor-only strategies are documented in ADR-0020 (defect guard, not a new deferred capability).
- 2026-05-11: Discrete benchmark trend rows and cold→warm acceptance evidence documented in ADR-0022 / PRD-0023.
