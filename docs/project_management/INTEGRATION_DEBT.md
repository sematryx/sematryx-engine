# Integration Debt

## Current Deferred Items

- Selector/memory recommendations remain domain-keyed only; using stored `descriptor_learning_features`
  to bucket or rank discrete-shaped histories is deferred.
- Hybrid **outer** loop: neighborhood refinement + staged inner budgets are integrated (ADR-0021); acquisition/Bayesian outer sampling and tighter global outer/inner budgeting heuristics remain deferred.
- Optional adapters for non-local backends (kept out of v1 core path).
- Expanded solver portfolio parity vs legacy project.
- Non-SciPy legacy continuous backends require optional package installation; calibration depth remains deferred.
- Full core-depth topology-to-solver integration and adaptive retry/tuning loop parity (runtime integrated; remaining debt is non-SciPy backends and broader parity benchmark matrix).
- Automated hyperparameter search grids / Bayesian tuning deferred beyond deterministic priors.
- Rich markdown/HTML explanation renderers are deferred; lightweight concise/verbose string helpers are now available.
- Longitudinal benchmark trend storage beyond generated snapshot files.
- `generate_benchmark_trend_report.py` does not yet emit discrete validation scenario rows (knapsack / assignment).
- Alternative reward transforms (e.g. log-scale) deferred pending analysis against objective snapshot metrics.

## Policy

Deferred items must be recorded here before being excluded from the current slice.

## Notes

- 2026-05-11: Continuous-path bandit exclusions for descriptor-only strategies are documented in ADR-0020 (defect guard, not a new deferred capability).
