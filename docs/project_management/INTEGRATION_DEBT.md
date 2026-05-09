# Integration Debt

## Current Deferred Items

- Mixed continuous + discrete routing in a single `optimize()` call remains deferred to the Stage 3 hybrid routing slice (discrete-only baseline is integrated).
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
