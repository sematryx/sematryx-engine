# Architecture Rule

- Any structural change to `src/sematryx_engine/engine/` or `src/sematryx_engine/solvers/` requires an ADR update under `docs/architecture/decisions/`.
- Keep local-first boundary strict: no cloud/runtime service dependencies in default engine path.
