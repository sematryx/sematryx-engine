# ADR-0026: Rename Shape Classifier; Record Topology-Pipeline Drift; Set Real-Pipeline Slice

## Status

Accepted

## Context

An audit of the engine's "topology pipeline" (PRD-0006 / ADR-0005 scaffold; PRD-0007 /
ADR-0006 Physarum-tunneling integration) found a wide gap between the documentation's
vocabulary and the code's behaviour.

What the engine actually has under those names:

- `engine/topology.py` (89 lines): receives only `bounds` and `max_evaluations`, never
  samples the objective, and computes a weighted sum of `dimensions`, `budget_per_dim`,
  and `span_variability`. The "Physarum tunneling score" is decoration over arithmetic
  on the input shape.
- `strategy_selector._topology_tunneling_override`: hardcodes `scipy_dual_annealing` with
  confidence `0.86` whenever the score crosses `0.75` or the directive is `"aggressive"`.

What the legacy api codebase (now deprecated, kept for reference) had under the same
names — see [`/home/workspace/sematryx-api/sematryx/core/optimizers/topology_pipeline.py`](../sematryx-api/sematryx/core/optimizers/topology_pipeline.py)
and siblings:

- ~2,278 lines across `decomposition.py` (Sobol sensitivity + dim reduction),
  `network_mapper.py` (`PhysarumNetworkMapper` building an actual landscape graph from
  objective samples), `tunneling.py` (`TopologyInformedTunneling` + `SHGOSubspaceProver`),
  and `topology_pipeline.py` (5-stage orchestrator that *uses* the network map to inform
  the tunneling solver).

PRD-0006 explicitly scoped the engine's slice to "kickoff scaffold — no routing change,
just artifact contract." PRD-0007 / ADR-0006 then added "Physarum tunneling" *names* to
fields in that scaffold and wired them to `scipy_dual_annealing` via metaphor, without
implementing any of the api's machinery. Subsequent docs (README, SYSTEM_OVERVIEW,
CHANGELOG) referred to the result as "the topology pipeline" — language load that the
code couldn't carry. The ablation harness's v2 "topology_routing feature helps" verdict
therefore measured a problem-shape classifier's effect on routing, not topology
machinery.

## Decision

1. **Rename the existing stub to reflect what it computes.** It classifies a problem by
   its problem-space shape — dimensions, bound widths, evaluations-per-dimension —
   *not* by any landscape topology. Specifically:

   | Old | New |
   |---|---|
   | `engine/topology.py` | `engine/problem_shape_classifier.py` |
   | `TopologyArtifact` | `ProblemShape` |
   | `build_topology_artifact()` | `build_problem_shape()` |
   | `physarum_tunneling_score` | `shape_routing_score` |
   | `tunneling_directive` | `shape_routing_directive` |
   | `OptimizationResult.topology_artifact` | `OptimizationResult.problem_shape` |
   | `AblationConfig.topology_routing` | `AblationConfig.shape_routing` |
   | `_topology_tunneling_override` | `_shape_routing_override` |
   | basis `"physarum_tunneling_override"` | basis `"shape_routing_override"` |
   | explanation key `topology_tunneling_directive` | `shape_routing_directive` |
   | explanation key `topology_physarum_tunneling_score` | `shape_routing_score` |
   | explanation key `topology_budget_regime` | `budget_regime` |
   | explanation key `topology_complexity_hint` | `complexity_hint` |
   | scenario `topology_firing_current` | `shape_routing_firing_current` |
   | parameter `tunneling_directive` in `tuning_priors` | `shape_routing_directive` |
   | parameter `topology_budget_regime` in `tuning_priors` | `budget_regime` |

2. **Preserve the word "topology" for the slice that actually does topology.** When the
   real pipeline is ported (Slice 1 below), it can claim the name honestly:
   `engine/topology_pipeline.py`, `PhysarumNetworkMapper`, etc.

3. **Mark prior scaffold artifacts as superseded.**
   - ADR-0005 (Topology Pipeline Scaffold): superseded — code renamed to
     problem-shape classifier; the "scaffold for a real topology pipeline" framing is
     replaced by an honest classifier scope.
   - ADR-0006 (Physarum Tunneling Integration): superseded — the
     `_shape_routing_override` retains the same hardcoded routing decision, but the
     "Physarum integration" claim is withdrawn (no Physarum machinery was implemented).
     The real integration is the next slice.
   - PRD-0006 (Topology Pipeline Kickoff) and PRD-0007 (Topology-Solver Integration
     with Physarum Tunneling): superseded by this ADR's correction. Their acceptance
     criteria are still satisfied at the stub level; the naming and framing are not.

4. **Establish Stage 4 Slice 1 as the real-pipeline port.** The original intent of
   PRD-0007 / ADR-0006 — "integrate Physarum mapping output into the tunneling solver
   path so the mapper's landscape characterisation actually informs solver decisions"
   — was never implemented in the engine. That is now the substance of Stage 4 Slice 1.
   The legacy api codebase's topology pipeline is the design source; the engine port
   must come under ablation gating so each piece earns its place rather than reproducing
   the api's drift.

## Alternatives Considered

- **Keep the names, change nothing.** Rejected: the documentation overclaims what the
  code does; future readers (human or AI) inherit the drift. The engine project's
  founding charter (PRD-0001) is "rebuild without drift," and keeping the misleading
  names violates that.
- **Build the real pipeline first, rename after.** Rejected: the rename is mechanical
  and reduces ambiguity *before* the real-pipeline work begins, so the new pipeline
  doesn't compete with the legacy stub for the same names. Doing the rename first lets
  the real `topology_pipeline.py` arrive clean.
- **Remove the stub entirely.** Considered. Rejected for now: the shape-routing
  override produces a measurable effect on the firing scenario (v2 baseline, +71% Δ),
  so the stub does *something*. Better to keep it under an honest name and decide
  during Slice 1 whether to retire it once the real pipeline is in.
- **Rename to `topology_problem_classifier` or similar.** Rejected. The classifier
  does not compute topology in any sense — bound widths are metric, eval budget is a
  solver constraint, dimension count is one weakly-topological scalar. The honest
  name is `problem_shape_classifier`.

## Consequences

- **Positive:**
  - Public API field names match implementation reality. New readers won't believe
    machinery exists that doesn't.
  - The word "topology" is freed for the real pipeline.
  - Stage 4 Slice 1 has a clean starting point: port the api's actual topology
    components (Sobol decomposition, Physarum network mapping, topology-informed
    tunneling, SHGO subspace prover) under ablation gating.
  - The audit's findings are recorded so this drift can't recur silently.

- **Negative:**
  - Wide rename touches 30 files (source, tests, docs). Mechanical, but visible.
  - Pre-rename baselines (`ablation_pre-stage-4.{json,md}` and
    `ablation_pre-stage-4-v2.{json,md}`) keep their pre-rename field names; the
    findings doc adds a note explaining the relabel and that the
    verdicts measured the stub, not topology machinery.
  - The ablation verdict "topology_routing feature helps" becomes
    "shape_routing feature helps" — same data, narrower claim.

- **Follow-up tasks:**
  - Stage 4 Slice 1: port the topology pipeline from the legacy api reference into the
    engine, under ablation gating, each piece independently measured. See ACTIVE_PLAN.
  - Decide post-port whether the shape-routing override stays alongside the real
    topology pipeline or gets retired.
  - When the real pipeline lands, write ADR-0027 documenting its design (sampling
    budget, network construction, tunneling solver wiring) with explicit
    measurement-driven rationale — the gap ADR-0006 left.
