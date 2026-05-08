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

Bandit learning state is persisted locally at `~/.sematryx/bandit_state.json` so
selection quality can improve across process restarts.

Bandit rewards from each run use `min(1, 1/(1+sqrt(best_value)))` for smoother updates across objective scales.

Each optimization result now includes a deterministic `topology_artifact` scaffold
(dimensions, span profile, budget regime, complexity hint) for Stage 4 topology integration.
The topology artifact now includes Physarum tunneling guidance and can directly influence
strategy selection for aggressive tunneling cases.

The repo additionally enforces planning and verification artifacts to reduce drift.

## Quick Start

```bash
pip install -e .[dev]
pytest
```

```bash
# Stage 2 benchmark suite
make benchmark

# JSON/Markdown trend snapshot (same metrics as performance tests)
make report-benchmark
```

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




