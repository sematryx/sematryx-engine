# ADR-0006: Physarum Signal Drives Tunneling Strategy

## Status

**Superseded by ADR-0026** (2026-05-13). This ADR's "Physarum integration" claim is
withdrawn — no Physarum machinery was implemented; the override only routes by
problem-shape signals (dimensions + budget + bound variability) and hardcodes
`scipy_dual_annealing`. The override's wiring is preserved under its honest name
(`_shape_routing_override`). The real Physarum → tunneling integration is Stage 4
Slice 1; see ADR-0026.

Originally: Accepted

## Context

The original topology solver did not consume Physarum-network output to inform tunneling. Stage 4
requires topology-driven routing decisions, and this missing link was explicitly called out as required.

## Decision

Extend the topology artifact with `physarum_tunneling_score` and `tunneling_directive`, then use
that signal in strategy selection. When the Physarum directive is aggressive (or score >= 0.75),
the selector routes to `scipy_dual_annealing` with explicit tunneling confidence.

## Alternatives Considered

- Keep topology data passive until later (rejected: does not resolve the required enhancement).
- Apply Physarum only as solver parameter tuning without routing (rejected: weak guarantee).

## Consequences

- Positive: topology now directly affects tunneling behavior in runtime selection.
- Negative: one deterministic override path can reduce bandit exploration for high-score cases.
