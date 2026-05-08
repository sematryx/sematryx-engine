# PRD-0007: Topology-Solver Integration with Physarum Tunneling

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
