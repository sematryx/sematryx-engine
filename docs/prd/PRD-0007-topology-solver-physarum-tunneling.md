# PRD-0007: Topology-Solver Integration with Physarum Tunneling

> **Status: Superseded by ADR-0026** (2026-05-13). The "Physarum tunneling" integration
> this PRD scoped was never implemented — no landscape mapping, no tunneling solver,
> no Physarum machinery. What shipped is a hardcoded "force `scipy_dual_annealing` when
> the shape-routing score crosses 0.75" override, now correctly named
> `_shape_routing_override`. The real integration (port the legacy api's `PhysarumNetworkMapper`
> and `TopologyInformedTunneling` into the engine, wire mapper → solver) is Stage 4
> Slice 1. See ADR-0026 and the reshaped ACTIVE_PLAN entry.

## Problem Statement

Topology artifacts were generated but not used for routing. A required enhancement is to integrate
Physarum-network output so tunneling behavior is informed by topology.

## Goals

- Extend topology artifact with explicit Physarum tunneling signal.
- Route aggressively tunneling cases to a tunneling-capable strategy.
- Add deterministic tests proving Physarum signal influences selection.

## Non-Goals

- No discrete solver changes.
- No new external network/service dependencies.

## Functional Requirements

- `build_topology_artifact` emits `physarum_tunneling_score` and `tunneling_directive`.
- `StrategySelector.select` accepts `topology_artifact` and applies Physarum override.
- `run_optimization` passes topology artifact into selector.

## Acceptance Criteria (Checklist)

- [x] Physarum fields are present in topology artifact with stable schema.
- [x] Aggressive Physarum directive routes to tunneling strategy (`scipy_dual_annealing`).
- [x] Unit + integration tests cover new behavior.
- [x] Governance artifacts updated (ADR/VR/plan/changelog/debt).

## Verification Link

`docs/process/verification/VR-0007-topology-solver-physarum-tunneling.md`
