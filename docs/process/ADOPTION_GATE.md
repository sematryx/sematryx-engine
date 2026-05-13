# Adoption Gate

Use this gate before integrating any new subsystem/module into the runtime path.

## Required Decision Inputs

1. Candidate component and intended runtime touchpoints.
2. Explicit hypothesis with measurable outcome (quality, stability, or cost).
3. Benchmark scenarios and baseline metrics to compare against.
4. Pre-declared go/no-go thresholds.

## Required Execution Steps

1. Create a PRD for the trial scope and acceptance thresholds.
2. Implement a bounded integration trial behind clear wiring points.
3. Run baseline vs candidate benchmarks using reproducible seeds.
4. Add integration tests proving runtime-path wiring.
5. Record go/no-go decision with evidence and rationale.

## Required Artifacts

- New `PRD-*.md` and `VR-*.md` files for each trial slice.
- New ADR when core behavior or architecture changes.
- Updated `INTEGRATION_DEBT.md` if component is deferred/rejected.

## Decision Log

| Date | Candidate | Hypothesis | Outcome | Decision | Evidence |
|------|-----------|------------|---------|----------|----------|
| YYYY-MM-DD | `<component>` | `<metric target>` | `<result>` | Go / No-Go / Defer | PRD/VR/bench links |

## Engine vs Legacy-API Registry

This registry tracks every named subsystem from the deprecated sematryx-api codebase
(see `/home/workspace/sematryx-api/`) against its current implementation status in the
engine. Established by ADR-0027 in response to the topology-pipeline drift incident
(ADR-0026), where the engine inherited vocabulary from sematryx-api without porting
substance.

**The substance gate in `scripts/check_policy.py` enforces:** any PR that introduces
identifiers from `LEGACY_API_VOCABULARY` into engine source code must update this
file with an explicit `port` / `defer` / `drop` decision for each new term. New rows
are added when an audit surfaces additional terms. Status transitions (e.g. `stub` →
`partial-port` → `fully-ported`) require a CHANGELOG entry and, if behaviour changes,
an ADR.

### Status meanings

- **stub** — name present in engine; implementation is trivial / problem-shape only / not what the name implies. Should be renamed (per ADR-0026 pattern) or ported.
- **partial-port** — engine has *some* of the api's machinery, but not all. Acceptable interim state; track remaining gaps.
- **fully-ported** — engine matches the api's substance for this subsystem. Closed item.
- **deferred** — explicitly out of v1 scope; tracked in `INTEGRATION_DEBT.md`. Engine source must not use the vocabulary; rename if needed.
- **dropped** — not part of the local pip product. Engine docs and code must not reference the vocabulary at all.
- **renamed** — engine code formerly used the vocabulary, now renamed (e.g., `topology_artifact` → `problem_shape`). Engine surface is clean; the real implementation may be future work, tracked separately.

### Registry

| Subsystem | API reference | API LOC | Engine impl | Engine LOC | Status | Decision rationale | Last verified |
|---|---|---|---|---|---|---|---|
| Topology pipeline (Sobol decomposition, Physarum mapping, topology-informed tunneling, SHGO subspace prover) | `sematryx-api/sematryx/core/optimizers/{topology_pipeline,decomposition,network_mapper,tunneling}.py` | ~2,278 | engine has only `problem_shape_classifier.py` (formerly `topology.py`); no landscape sampling, no graph, no tunneling solver | 89 (classifier only) | **renamed** (stub) + **port deferred to Stage 4 Slice 1** | Stage 4 Slice 1 ports this from api under ablation gating, each piece independently. See ADR-0026, ADR-0027. | 2026-05-13 |
| Contextual bandit (Thompson sampling + per-arm Bayesian linear regression + context features from problem characteristics + Qdrant-gated confidence) | `sematryx-api/sematryx/core/optimizers/strategy_bandit.py` | ~2,460 | flat per-arm `Beta(α, β)` Thompson sampling; zero context dimension | 67 | **stub** | "Contextual" claim withdrawn. Engine retains a flat bandit. Whether to port the full contextual machinery is a v1-scope decision. | 2026-05-13 |
| Meta-learning across problems | `sematryx-api/sematryx/core/learning/meta_learning.py` | ~500 | absent | 0 | **decision needed** | Not started in engine. Likely deferred for v1 unless a specific user need surfaces. | 2026-05-13 |
| Transfer learning | `sematryx-api/sematryx/core/learning/transfer.py` | ~1,082 | absent | 0 | **decision needed** | Not started in engine. | 2026-05-13 |
| Learning persistence (Qdrant-backed) | `sematryx-api/sematryx/core/learning/persistence.py` | ~379 | engine has `LocalStrategyMemory` (SQLite domain-string lookup) | 166 | **partial-port** (different backend) | Engine deliberately uses SQLite for local-first. Qdrant integration would violate the local-first boundary; do not port. | 2026-05-13 |
| Vector memory | `sematryx-api/sematryx/memory_knowledge/vector_memory/` | (part of ~8,394 in memory_knowledge/) | absent | 0 | **decision needed** | Pulls in vector DB dependency — likely **drop** for local-first v1. | 2026-05-13 |
| Knowledge graph | `sematryx-api/sematryx/memory_knowledge/knowledge_graph/` | (part of ~8,394) | absent | 0 | **decision needed** | Likely **drop** for local-first v1 unless there's a specific use case. | 2026-05-13 |
| Temporal intelligence | `sematryx-api/sematryx/memory_knowledge/temporal_intelligence/` | (part of ~8,394) | absent | 0 | **decision needed** | Likely **drop** for local-first v1. | 2026-05-13 |
| AI module (adaptive improvement, causal discovery, federated learning, neural-symbolic, meta-policy, cross-problem learning) | `sematryx-api/sematryx/core/ai/` | ~31,251 total | absent | 0 | **decision needed** | Almost certainly **drop** most for v1. Each individual subsystem may have a port/defer/drop decision later. | 2026-05-13 |
| Explainability architecture (6-stage explanatory artifacts: competitive regions, sensitivity rankings, basin connectivity, barrier profiles, optimality certificates, historical context, confidence levels) | `sematryx-api/sematryx/platform_services/{temporal,async}_explainability.py` + `docs/architecture/EXPLAINABILITY_ARCHITECTURE.md` | ~1,151 + design doc | engine has `explanation_formatter.py` (key-printing) + `explanation` dict in results | 71 | **stub** | Engine emits metadata, not reasoning. "Explanation payload" claim narrowed in PR 5 README; further narrowing may be needed. Real explainability is a future slice. | 2026-05-13 |
| Domain libraries (financial, healthcare, supply_chain, ai_ml, marketing) | `sematryx-api/sematryx/domain_libraries/` | 5 × ~1,500 LOC | absent | 0 | **deferred** | Not part of v1 engine scope. May ship as separate pip packages (e.g. `sematryx-financial`) later. Engine core stays domain-agnostic. | 2026-05-13 |
| Autodidactic / self-improving optimizers | `sematryx-api/examples/self_improving_api.py` + various `core/ai/learning/`, `specialized_optimizers/self_improving/` | varied | engine has multi-attempt fallback loop labeled "autodidactic"; no actual learning across attempts | — | **stub** (name only) | "Autodidactic" claim is overstated for the engine's loop. Either rename or implement actual adaptation. Tracked for renaming. | 2026-05-13 |

### How to update this registry

1. **New audit finds a term in api that the engine could plausibly inherit:** add the term to `LEGACY_API_VOCABULARY` in `scripts/check_policy.py`, add a row here with status `decision needed`.
2. **A PR introduces an api term into engine code:** the substance gate fails CI. Update this registry with the port/defer/drop decision before the PR can land.
3. **Status changes (stub → partial → full, or port → drop):** CHANGELOG entry required; ADR required if the change affects runtime behaviour.
4. **A row is fully closed (fully-ported with verification, or dropped permanently):** keep the row for historical record. Do not delete rows.
