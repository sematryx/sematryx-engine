# System Overview

```mermaid
flowchart LR
    U[User Code] --> API[sematryx_engine.api.optimize]
    API --> OPT[Engine Optimizer]
    OPT --> FEAT[Problem Features]
    OPT --> SEL[Strategy Selector]
    SEL --> MEM[(Local Strategy Memory SQLite)]
    SEL --> BANDIT[Contextual Bandit]
    BANDIT --> BANDIT_STATE[(Bandit State JSON)]
    OPT --> SOLV[SciPy Solvers]
    SOLV --> RES[Optimization Result]
    OPT --> MEM
    RES --> EXP[Explanation Metadata]
```

## Boundaries

- Local-first runtime: no required cloud dependencies in core path.
- Strategy memory and learning are persisted locally.
- Integrations beyond local runtime must be optional adapters.
