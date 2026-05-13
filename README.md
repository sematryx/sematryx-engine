# sematryx-engine

Local-first optimization engine, pip-installable. Picks an optimization strategy
from a registered roster, runs it (optionally multi-attempt), records the result in
local persistence, and returns a structured result with decision metadata.

## What it does today

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

Three execution paths, selected by input shape:

- **Continuous-only** (`bounds=...`) — strategy picked from SciPy family (DE, dual
  annealing, SHGO, L-BFGS-B, Powell, TNC, SLSQP, COBYLA, Nelder-Mead, CG) plus
  optional non-SciPy backends (CMA-ES, scikit-optimize) when installed. Multi-attempt
  loop runs 1–3 attempts based on budget regime and keeps the best.
- **Discrete-only** (`variable_descriptors=...` with `integer`/`categorical` types) —
  routes to `discrete_random_neighborhood` baseline (random search + coordinate
  neighborhood refinement).
- **Mixed** (descriptors with both continuous + discrete) — routes to
  `hybrid_outer_random_inner_scipy`: LCB acquisition over discrete shells + inner
  SciPy continuous solve per shell + neighborhood refinement.

Bandit state and strategy memory persist under `~/.sematryx/` so selection quality
can improve across process restarts. Variable descriptors support continuous,
integer, and categorical types.

## What's substantive vs stub

Engineering audit finished 2026-05-13 (see ADR-0026 / ADR-0027). The
[Current Substance State table in SYSTEM_OVERVIEW.md](docs/architecture/SYSTEM_OVERVIEW.md#current-substance-state)
is the canonical record. Short version:

| Subsystem | Status |
|---|---|
| Solver roster + dispatch | substantive |
| Strategy selector (filter + override + bandit fallback) | substantive |
| Hybrid solver (LCB + refinement) | substantive |
| Variable descriptor validation + routing | substantive |
| Ablation harness | substantive |
| Problem-shape classifier | substantive *for what it claims* (problem-space shape, not landscape topology) |
| Tuning priors | partial (works in aggregate; the `domain` input is currently a hash with no semantic meaning) |
| Multi-attempt loop | substantive mechanism; "autodidactic" naming is overstated and tracked for rename |
| Bandit | stub — flat Thompson sampling, no context features (claim "contextual bandit" was withdrawn) |
| Strategy memory | partial — SQLite domain-string lookup; problem features are stored but not used for ranking |
| Decision metadata (`result.explanation`) | stub — trace metadata, not reasoning. Formatter helpers print keys |
| Benchmark snapshots | substantive snapshots; the "trend report" claim was overstated — no time-series |
| Topology pipeline (Physarum mapping + topology-informed tunneling) | **not implemented** — the engine has a problem-shape classifier under that name historically; the real pipeline is Stage 4 Slice 1 work |

## Relationship to sematryx-api

sematryx-api is **deprecated**. sematryx-engine is the pip-installable replacement.
The engine does not depend on the api, does not import from it, and is not required
to maintain parity.

Some vocabulary in the engine (`physarum`, `tunneling`, `autodidactic`, etc.) was
historically inherited from the api codebase without porting the substance. The
[Engine vs Legacy-API Registry](docs/process/ADOPTION_GATE.md#engine-vs-legacy-api-registry)
records every such term with an explicit `port` / `defer` / `drop` decision.
`scripts/check_policy.py` blocks PRs that introduce api vocabulary into engine
source without a registry decision.

## Quick start

```bash
pip install -e ".[dev]"
make all  # lint + typecheck + tests + policy checks
```

CI status checks: `lint`, `typecheck`, `unit-smoke`, `integration-performance`,
`policy`. The aggregate gate `CI / required-checks` must be green to merge.

## Governance

This repo runs a rigorous PRD → ADR → VR loop with mechanical CI enforcement of
required artefacts (see
[`docs/process/DEVELOPMENT_WORKFLOW.md`](docs/process/DEVELOPMENT_WORKFLOW.md) and
[`docs/process/DEFINITION_OF_DONE.md`](docs/process/DEFINITION_OF_DONE.md)). A
substance gate (ADR-0027) additionally blocks the introduction of legacy api
vocabulary into engine source without a registry decision.

If you're an AI session, **start with [`CLAUDE.md`](CLAUDE.md).**

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — top-of-context doc; what this project is, hard rules
- [`docs/architecture/SYSTEM_OVERVIEW.md`](docs/architecture/SYSTEM_OVERVIEW.md) — architecture + current substance state
- [`docs/planning/ACTIVE_PLAN.md`](docs/planning/ACTIVE_PLAN.md) — current phase, next slices
- [`docs/process/ADOPTION_GATE.md`](docs/process/ADOPTION_GATE.md) — registry + adoption gate
- [`docs/process/DEVELOPMENT_WORKFLOW.md`](docs/process/DEVELOPMENT_WORKFLOW.md) — workflow
- [`docs/process/DEFINITION_OF_DONE.md`](docs/process/DEFINITION_OF_DONE.md) — done gates including substance gates
- [`docs/architecture/decisions/`](docs/architecture/decisions/) — ADRs

## Bench + ablation

```bash
make benchmark          # selection + objective benchmark snapshots
make report-benchmark   # render JSON + Markdown trend snapshot

make ablation           # ablation matrix, light (4 scenarios × 8 knobs × 20 seeds)
make ablation-full      # ablation matrix, heavy (N=100, on-demand, ~15 min)
```

Ablation reports land under
[`docs/process/verification/baselines/`](docs/process/verification/baselines/).
