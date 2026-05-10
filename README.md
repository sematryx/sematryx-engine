# sematryx-engine

Local-first optimization engine package for Sematryx.

## Goals

- Minimal, maintainable core runtime
- No required cloud infrastructure for default execution
- Deterministic testable optimization path
- Pluggable local learning persistence

## Governance

This repository uses enforced policy checks, ADR requirements for architecture changes,
and forbidden-import checks to keep a strict local-first boundary.

Learning behavior includes a deterministic memory override when enough local evidence
exists for a domain strategy, with bandit selection remaining the default path.
Discrete-only and hybrid runs additionally record descriptor-shape statistics and the
clipped bandit reward on each SQLite memory row (`features_json`).

Bandit learning state is persisted locally at `~/.sematryx/bandit_state.json` so
selection quality can improve across process restarts.

Bandit rewards from each run use `min(1, 1/(1+sqrt(best_value)))` for smoother updates across objective scales.

Each optimization result now includes a deterministic `topology_artifact` scaffold
(dimensions, span profile, budget regime, complexity hint) for Stage 4 topology integration.
The topology artifact now includes Physarum tunneling guidance and can directly influence
strategy selection for aggressive tunneling cases.
Optimization results also include a structured `explanation` payload describing selection basis,
confidence, and topology-tunneling evidence.
The continuous strategy roster now includes additional SciPy methods (`shgo`, `powell`, `tnc`,
`slsqp`, `cobyla`, `nelder-mead`, `cg`) beyond DE/dual-annealing/L-BFGS-B.
Runtime now supports a bounded autodidactic retry loop (1-3 attempts based on topology budget regime),
selecting the best attempt and exposing attempt trace data in `explanation`.
Solver hyperparameter priors are computed deterministically from domain label, problem complexity,
and topology regime and are reflected in explanations alongside per-attempt evaluation budgets.
Explanations additionally expose an adaptation overlay tying topology hints, problem feature summaries,
retry sequencing, and the winning attempt index.
A parity-oriented integration regression gate validates benchmark snapshot thresholds and
runtime contract completeness across topology + adaptation + tuning-prior surfaces.
Optional non-SciPy continuous backends (CMA-ES and scikit-optimize families) are wired behind
runtime availability checks so default installs remain lightweight.
Concise and verbose explanation formatter helpers are exported for quick human-readable summaries.
Typed variable descriptors are accepted by the API: continuous-only lists run the SciPy-centric portfolio; discrete-only lists (`integer`/`categorical`) run the `discrete_random_neighborhood` baseline; mixed continuous + discrete lists run `hybrid_outer_random_inner_scipy` (random discrete exploration, then discrete coordinate neighborhood refinement, with inner continuous solves per shell).

The repo additionally enforces planning and verification artifacts to reduce drift.

## Quick Start

```bash
pip install -e .[dev]
pytest
# Full parity with CI (integration + performance; avoids duplicate test module name clash):
# pytest tests/integration tests/performance --import-mode=importlib
```

```bash
# Stage 2 benchmark suite (+ Stage 3 discrete validation scenarios)
make benchmark

# JSON/Markdown trend snapshot (same metrics as performance tests)
make report-benchmark
```

Optional `rng_seed` on `optimize()` fixes randomness for discrete-only and hybrid outer loops (SciPy
inner solves keep their own seeds).

Bounds-only continuous runs automatically exclude discrete/hybrid strategy arms from bandit
selection (those strategies require `variable_descriptors`).

Snapshots include selection scenarios plus isolated scipy sphere runs (`version` 2, `objectives` section).

```python
from sematryx_engine import optimize

def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)

result = optimize(
    objective_function=sphere,
    bounds=[(-5.0, 5.0), (-5.0, 5.0)],
    max_evaluations=100,
)
print(result.best_value)
```




