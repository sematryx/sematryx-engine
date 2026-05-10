# PRD-0018: Stage 3 Hybrid Routing (Mixed Discrete + Continuous)

## Problem Statement

Mixed `variable_descriptors` lists previously failed fast; users need one-call optimization when continuous and discrete dimensions coexist.

## Goals

- Route mixed problems through an explicit hybrid pipeline documented in results.
- Keep discrete-only and continuous-only paths unchanged.
- Prevent hybrid **inner** SciPy selection from choosing discrete-only strategies.

## Non-Goals

- Globally optimal mixed-integer guarantees or MILP integration.
- Tunable outer-loop bayesian search beyond random discrete draws (future slices).

## Functional Requirements

- Outer loop samples feasible discrete assignments; inner loop optimizes continuous coordinates with existing strategy dispatch + tuning priors.
- Topology/features computed on full encoded bounds; inner strategy selection uses continuous-subproblem features.
- Explanation adaptation exposes inner strategy name and selection basis.

## Acceptance Criteria (Checklist)

- [x] Mixed descriptors run without raising; strategy `hybrid_outer_random_inner_scipy` recorded.
- [x] Inner selector excludes `discrete_random_neighborhood` and hybrid composite arm.
- [x] Unit + integration tests cover merge helpers and end-to-end hybrid optimize.
- [x] Governance artifacts updated.

## Verification Link

`docs/process/verification/VR-0018-stage3-hybrid-routing.md`
