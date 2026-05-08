# ADR-0002: Benchmark Metrics Module in Engine

## Status

Accepted

## Context

Performance tests duplicated selection benchmark logic. Trend reporting needs the same
metrics as tests without copying code. The module must remain local-first and avoid new
optional backends.

## Decision

Add `sematryx_engine.engine.benchmark_metrics` with:

- `run_selection_benchmark` / `SelectionBenchmarkResult` for cold vs warm measurement.
- `collect_domain_benchmark_snapshot` for bundled scenario snapshots used by CLI and tests.

Reporting is invoked offline via `scripts/generate_benchmark_trend_report.py` and does not
change default optimization API behavior.

## Alternatives Considered

- Keep logic only in tests (rejected: duplication vs reporting script).
- New top-level `benchmarks` package (rejected: avoid new subsystem until adoption gate).

## Consequences

- Positive: single source of truth for benchmark numbers; easier calibration slices.
- Negative: engine package grows slightly; snapshot runs duplicate selector work at scale.
