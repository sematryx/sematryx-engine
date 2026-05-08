# ADR-0011: Explainability Adaptation Depth in Optimization Results

## Status

Accepted

## Context

Structured explanations exposed strategy basis and attempts but lacked a compact adaptation overlay tying
topology, problem features, planned retries, and the winning attempt index together.

## Decision

Extend optimizer explanations with an `adaptation` dictionary capturing topology regime hints,
problem complexity signals, global budgets, ordered retry strategies, and the winning attempt ordinal.

## Alternatives Considered

- Separate explain-only RPC/logging pipeline (rejected: weak ergonomics for local-first Python callers).
- Long prose summaries only (rejected: harder for deterministic testing).

## Consequences

- Positive: auditors/tests can validate adaptation rationale alongside tuning priors.
- Negative: explanation payloads continue growing—consumers must treat unknown keys forward-compatibly.
