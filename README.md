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

The repo additionally enforces planning and verification artifacts to reduce drift.

## Quick Start

```bash
pip install -e .[dev]
pytest
```

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
