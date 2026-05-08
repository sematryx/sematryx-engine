# ADR-0004: Benchmark Objective Metrics in Snapshot

## Status

Accepted

## Context

Selection hit-rate benchmarks alone cannot detect regressions in solver output quality.
The trend snapshot needs comparable objective metrics without coupling to user home-directory
runtime state.

## Decision

Extend `collect_domain_benchmark_snapshot` to version `2` by adding `objectives` with
two isolated sphere runs (`sphere_dim4`, `sphere_dim8`) using dedicated SQLite and bandit
JSON paths under a caller-provided temporary directory.

## Alternatives Considered

- Separate report command only (rejected: snapshot used for integration regression).
- Reuse global `~/.sematryx` paths (rejected: non-deterministic cross-run leakage).

## Consequences

- Positive: CI/integration can assert objective bands alongside selection metrics.
- Negative: Snapshot generation takes longer due to two scipy solves.
