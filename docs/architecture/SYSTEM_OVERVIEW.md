# System Overview

```mermaid
flowchart LR
    U[User Code] --> API[sematryx_engine.api.optimize]
    API --> OPT[Engine Optimizer]
    OPT --> FEAT[Problem Features]
    OPT --> TOPO[Topology Artifact + Physarum Signal]
    OPT --> SEL[Strategy Selector]
    SEL --> MEM[(Local Strategy Memory SQLite)]
    SEL --> BANDIT[Contextual Bandit]
    BANDIT --> BANDIT_STATE[(Bandit State JSON)]
    OPT --> SOLV[SciPy Solver Roster]
    OPT --> LOOP[Bounded Autodidactic Loop]
    OPT --> PRI[Tuning Priors]
    SOLV --> RES[Optimization Result]
    OPT --> MEM
    RES --> EXP[Structured Explanation Metadata]
    GEN[Benchmark report CLI] --> BMET[benchmark_metrics]
    BMET -. selection scenarios .-> SEL
    BMET -. objective snapshots .-> SOLV
```

## Boundaries

- Local-first runtime: no required cloud dependencies in core path.
- Strategy memory and learning are persisted locally.
- Integrations beyond local runtime must be optional adapters.
- Reported selection confidence reflects posterior belief or evidence-scaled memory override.
- Offline benchmark snapshots use `benchmark_metrics` and the report CLI without affecting live optimize paths.
- Snapshot version 2 adds reproducible objective-quality rows (isolated memory/bandit paths + scipy solve).
- Stage 4 topology integration consumes Physarum signal to inform tunneling-oriented strategy routing.
- Result payload includes structured explanation schema (basis/confidence + topology evidence).
- Continuous roster now includes multiple SciPy local/global methods to improve Stage 4 routing surface.
- Optimizer can execute bounded topology-budgeted retries and return per-attempt rationale in explanations.
- Deterministic tuning priors scale SciPy budgets/settings before each attempt and are echoed in explanations.
- Explanations include adaptation overlays referencing topology/problem summaries plus retry winners.
