# ADR-0013: Optional Non-SciPy Continuous Backends

## Status

Accepted

## Context

Stage 4 parity includes non-SciPy continuous solvers from the legacy roster, but local environments may
not always have optional dependencies installed.

## Decision

Add optional strategy wiring for CMA-ES and scikit-optimize families behind availability detection.
The selector roster includes these strategies only when packages are installed, while dispatch routes
non-`scipy_` strategies to a dedicated optional backend module.

## Alternatives Considered

- Require optional backends for all installs (rejected: violates lightweight local-first default).
- Keep optional backends fully deferred (rejected: blocks Stage 4 parity progress).

## Consequences

- Positive: richer strategy breadth without forcing extra dependencies by default.
- Negative: behaviour differs by environment depending on installed extras.
