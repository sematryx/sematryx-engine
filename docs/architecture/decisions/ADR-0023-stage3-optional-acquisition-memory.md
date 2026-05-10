# ADR-0023: Stage 3 Optional Closure — Hybrid LCB Acquisition + Descriptor-Mix Memory

## Status

Accepted

## Context

`ACTIVE_PLAN` listed optional follow-ups: acquisition-style hybrid outer search beyond uniform +
neighborhood refinement, descriptor-learning keyed recommendations, and tightening outer/inner
budget heuristics.

## Decision

1. **Hybrid outer acquisition:** Maintain per-shell statistics `(best_y, visits)` for evaluated
   discrete assignments. Each exploration step builds a candidate pool (random unseen shells +
   neighbors of the incumbent) and evaluates the shell minimizing an **LCB-style score**
   `best_y - k·sqrt(log(t+1)/(visits+0.5))`, with an optimism offset for unvisited keys.
   Refinement evaluates unseen neighbors sorted by the same score.
2. **Inner budgets:** Exploration uses `_inner_budget_explore` (sqrt-shaped cap vs remaining);
   refinement keeps `_inner_budget_refine` with slightly raised refinement floor.
3. **Result message:** `OptimizeResult.message` = `hybrid_outer_acquisition_lcb_inner_scipy_refined`.
4. **Memory:** `get_strategy_recommendations(..., descriptor_mix=...)` filters via
   `json_extract(features_json, '$.descriptor_mix')`; empty filtered aggregate falls back to
   domain-only. Hybrid inner `select_with_basis` passes `memory_descriptor_mix="mixed"`.

## Alternatives Considered

- Full Gaussian-process or Thompson sampling outer loop (deferred: dependency + calibration cost).
- Separate acquisition micro-package (rejected: keep solver-local helpers).

## Consequences

- Positive: measurable exploitation/exploration balance without new dependencies; mixed histories no
  longer masked by unrelated domain rows when picking inner SciPy arms.
- Negative: requires SQLite JSON1 (`json_extract`); bundled SQLite in supported Python builds is sufficient.
