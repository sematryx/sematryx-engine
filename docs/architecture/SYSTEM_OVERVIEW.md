# System Overview

```mermaid
flowchart LR
    U[User Code] --> API[sematryx_engine.api.optimize]
    API --> VD[Variable Descriptor Validation]
    VD --> OPT[Engine Optimizer]
    OPT --> FEAT[Problem Features]
    OPT --> SHAPE[Problem-Shape Classifier]
    OPT --> SEL[Strategy Selector]
    SEL --> MEM[(Local Strategy Memory SQLite)]
    SEL --> BANDIT[Contextual Bandit]
    BANDIT --> BANDIT_STATE[(Bandit State JSON)]
    OPT --> SOLV[Solver Roster (SciPy + Optional)]
    OPT --> LOOP[Bounded Autodidactic Loop]
    OPT --> PRI[Tuning Priors]
    SOLV --> RES[Optimization Result]
    OPT --> MEM
    RES --> EXP[Structured Explanation Metadata]
    EXP --> FMT[Formatter Helpers]
    GEN[Benchmark report CLI] --> BMET[benchmark_metrics]
    BMET -. selection scenarios .-> SEL
    BMET -. objective snapshots .-> SOLV
    VAL[Core-depth validation tests] -. regression gates .-> OPT
```

## Boundaries

- Local-first runtime: no required cloud dependencies in core path.
- Strategy memory and learning are persisted locally; discrete/hybrid runs record descriptor-shape
  features and bandit reward metadata in the JSON feature blob.
- Integrations beyond local runtime must be optional adapters.
- Reported selection confidence reflects posterior belief or evidence-scaled memory override.
- Offline benchmark snapshots use `benchmark_metrics` and the report CLI without affecting live optimize paths; snapshots include discrete cold/warm selection scenarios and seeded knapsack/assignment objective rows alongside sphere cases.
- Stage 3 discrete validation adds knapsack- and assignment-shaped scenarios (`discrete_benchmark_scenarios`)
  exercised in integration tests and `make benchmark`.
- Snapshot version 2 adds reproducible objective-quality rows (isolated memory/bandit paths + scipy solve).
- Problem-shape classifier (`build_problem_shape`) emits a deterministic shape-routing
  score + directive from bounds and budget. When the score crosses 0.75 or the directive
  is `aggressive`, the selector's shape-routing override forces `scipy_dual_annealing`.
  This is **not** a topology pipeline — see ADR-0026. The real topology pipeline is
  Stage 4 Slice 1.
- Result payload includes structured explanation schema (basis/confidence + shape-routing evidence).
- Continuous roster now includes multiple SciPy local/global methods to improve Stage 4 routing surface.
- Optimizer can execute bounded shape-budgeted retries (attempt count derived from `budget_regime`) and return per-attempt rationale in explanations.
- Deterministic tuning priors scale SciPy budgets/settings before each attempt and are echoed in explanations.
- Explanations include adaptation overlays referencing problem-shape summaries plus retry winners.
- Core-depth validation tests gate benchmark thresholds and runtime contract parity fields.
- Optional non-SciPy backends are included only when corresponding packages are installed.
- Concise/verbose formatter helpers summarize explanation payloads for CLI/notebook workflows.
- Typed variable descriptors are validated at API entry; discrete-only runs (`integer`/`categorical`) use `discrete_random_neighborhood`; mixed continuous + discrete runs use `hybrid_outer_random_inner_scipy` with inner continuous strategy selection excluding discrete-only arms.
- Bounds-only continuous runs exclude discrete/hybrid strategy IDs from bandit selection so routing stays compatible with `solve_with_strategy`.
- Mixed hybrid runs use **LCB acquisition** over discrete shells (random + incumbent neighbors),
  then sorted neighbor refinement (inner SciPy per shell), with deduplicated discrete assignments.
- Hybrid inner continuous strategy selection may consult SQLite memory scoped by `descriptor_mix`
  (`json_extract` on stored feature JSON).
