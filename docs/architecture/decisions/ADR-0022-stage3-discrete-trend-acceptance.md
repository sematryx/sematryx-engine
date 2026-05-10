# ADR-0022: Discrete Cold→Warm Selection Metrics + Trend Snapshot Rows

## Status

Accepted

## Context

Stage 3 acceptance criterion 3 requires evidence that **strategy selection quality improves from
cold to warm history on discrete benchmarks**. Trend reporting (`generate_benchmark_trend_report.py`)
and `INTEGRATION_DEBT` still lacked discrete objective rows alongside sphere snapshots.

## Decision

1. Extend `collect_domain_benchmark_snapshot` with **discrete_selection** scenarios:
   - `discrete_knapsack` and `discrete_assignment2x2` cold/warm rows using domain keys
     `stage3_trend_knapsack01` / `stage3_trend_assignment2x2`, bounds matching encoded discrete
     toy specs, warm target `discrete_random_neighborhood`.
2. Extend `collect_objective_benchmark_snapshot` with **seeded** `solve_discrete_baseline` runs for
   knapsack-01 and assignment 2×2 (same RNG seeds as validation integration tests).
3. Teach `generate_benchmark_trend_report.py` to render **all** scenario and objective keys
   (sorted) so new rows appear without hardcoding.
4. Add integration tests proving warm mean confidence and hit rate exceed cold for acceptance
   domains (`test_stage3_discrete_cold_warm_selection`).

## Consequences

- Positive: one JSON/Markdown artifact covers continuous + discrete selection quality and discrete
  objective checks.
- Negative: full snapshot collection adds selection iterations (mitigated by shared `runs` default).
