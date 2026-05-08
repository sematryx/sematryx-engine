# ADR-0010: Local Hyperparameter Priors from Domain and Topology

## Status

Accepted

## Context

Stage 4 requires adaptive solver behaviour aligned with problem topology and domain identity without
introducing cloud-hosted tuning services.

## Decision

Introduce deterministic solver tuning priors computed from domain label (stable anchor),
problem-feature complexity, and topology regime/directives. Apply scaled evaluation budgets per autodidactic attempt,
adjust SciPy knobs (`dual_annealing` restart ratio, `differential_evolution` polish/population scale,
`shgo` sampling scale), and expose the prior snapshot on optimization explanations.

## Alternatives Considered

- External hyperparameter search service (rejected: violates local-first boundary).
- Randomised tuning draws (rejected: hurts deterministic benchmark reproducibility).

## Consequences

- Positive: richer solver behaviour with traceable rationale for audits/tests.
- Negative: priors must be regression-tested when SciPy defaults shift between releases.
