# ADR-0005: Topology Pipeline Scaffold

## Status

Accepted

## Context

Stage 4 requires topology-driven solver routing and adaptation, but the current engine has no
first-class topology artifact produced at runtime.

## Decision

Introduce a local, deterministic topology scaffold in `engine/topology.py` and attach the artifact
to `OptimizationResult` for every run. This kickoff slice does not change strategy selection or solver
routing behavior; it only establishes a stable artifact contract.

## Alternatives Considered

- Delay topology artifact until routing implementation (rejected: no stable contract to test against).
- Persist topology externally in files/DB (rejected: unnecessary I/O and complexity for kickoff).

## Consequences

- Positive: Stage 4 follow-up slices can consume a known topology payload.
- Negative: Slightly larger result payload and one extra computation per run.
