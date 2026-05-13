# Verification Report: Stage 4 Ablation Harness

## Reference

- PRD: `docs/prd/PRD-0025-stage4-ablation-harness.md`
- ADR(s):
  - `docs/architecture/decisions/ADR-0024-stage4-ablation-harness.md` (verdict rule)
  - `docs/architecture/decisions/ADR-0025-ablation-warmup-and-firing-scenarios.md` (warmup methodology + firing scenarios)
  - `docs/architecture/decisions/ADR-0026-rename-shape-classifier-and-record-topology-drift.md` (audit findings surfaced by the harness)

## Planned vs Implemented

For each PRD-0025 acceptance criterion:

- [x] **`AblationConfig` dataclass exists with the eight knobs and a `default()` classmethod** →
  `src/sematryx_engine/engine/ablation.py`. Knobs: `shape_routing`, `tuning_priors`,
  `autodidactic_loop`, `memory_override`, `descriptor_mix_memory`,
  `hybrid_outer_acquisition`, `hybrid_outer_refinement`, `continuous_bandit`. Unit
  tests: `tests/unit/test_ablation_config.py`.

- [x] **`optimize(...)` accepts `ablation` kwarg without altering default-path results** →
  `src/sematryx_engine/api/client.py` and `src/sematryx_engine/engine/optimizer.py`
  accept and thread the kwarg. Byte-identity integration test:
  `tests/integration/test_ablation_byte_identity.py` (3 paths × 3 seeds each).

- [x] **Each neutral fallback has a unit test proving the off-path is deterministic** →
  Per-knob fallback tests in `tests/unit/test_ablation_config.py` and
  `tests/unit/test_strategy_selector.py`. Hybrid and tuning-priors fallbacks have
  dedicated tests in `tests/unit/test_tuning_priors.py`.

- [x] **`run_ablation_matrix` returns a structured result usable by the report generator** →
  `src/sematryx_engine/engine/ablation_benchmark.py`. Integration test:
  `tests/performance/test_ablation_harness.py::test_light_matrix_runs_to_completion`.

- [x] **`scripts/generate_ablation_report.py` produces a JSON + Markdown report with verdict column** →
  Round-trip integration test:
  `tests/performance/test_ablation_harness.py::test_report_generator_round_trip`.

- [x] **`make ablation` and `make ablation-full` documented in `DEVELOPMENT_WORKFLOW.md`** →
  Makefile targets land; documented under the "Ablation Harness" section of
  `DEVELOPMENT_WORKFLOW.md`.

- [x] **Pre-Stage-4 baseline report committed; `ACTIVE_PLAN` Stage 4 preview notes the baseline** →
  `docs/process/verification/baselines/ablation_pre-stage-4-v2.{json,md}` +
  `FINDINGS-pre-stage-4-ablation.md`. ACTIVE_PLAN Slice 1 reshaped twice in response
  to the baseline (see entries dated 2026-05-12 and 2026-05-13).

- [x] **ADR-0024 records the ablation boundary, fallback semantics, and verdict thresholds** →
  ADR-0024 documents the verdict rule (direction + significance, no arbitrary
  effect-size thresholds) and the AblationConfig boundary.

- [x] **This VR documents byte-identity evidence, light-matrix runtime, and a snapshot of the baseline verdict table** → see below.

### Byte-identity evidence

`tests/integration/test_ablation_byte_identity.py` runs three paths (continuous,
discrete, hybrid) under three seeds each. For each pair, the optimizer is invoked
with `ablation=None` and then with `ablation=AblationConfig.default()`; the test
asserts `best_value`, `best_solution`, `evaluations`, and `strategy_used` match
byte-for-byte. All passed at PR 1 commit `915d114`.

### Light-matrix runtime

`make ablation` (light: 4 scenarios × 8 knobs × 20 seeds, plus per-(scenario, seed)
warmup phase for the warmed scenarios) completes in ~30 seconds on devbox. Target
was <3 minutes.

### Heavy baseline verdict snapshot (`ablation_pre-stage-4-v2`, N=100)

| Feature | Best scenario | Δ when off | p | Verdict |
|---|---|---|---|---|
| `shape_routing` | `shape_routing_firing_current` | +71.19% | <0.001 | feature helps |
| `autodidactic_loop` | `rugged_multimodal_8d` | +48.11% | <0.001 | feature helps |
| `tuning_priors` | `rugged_multimodal_8d` | +48.11% | <0.001 | feature helps |
| `hybrid_outer_refinement` | `hybrid_separating` | (load-bearing: 4 → ~0) | <0.001 | feature helps |
| `memory_override` | `rugged_multimodal_8d` (warmed) | 0% median, distributional | <0.001 | rank shift only |
| `continuous_bandit` | (none) | 0% | ≥0.473 | no effect |
| `descriptor_mix_memory` | (none) | 0% | 1.000 | no effect |
| `hybrid_outer_acquisition` | (none) | 0% | ≥0.577 | no effect |

Source: `docs/process/verification/baselines/ablation_pre-stage-4-v2.md`.

## Commands Run

```bash
make all                              # lint + typecheck + unit-smoke + policy
pytest tests/integration tests/performance --import-mode=importlib
make ablation                         # light matrix
make ablation-full                    # heavy matrix (used for v2 baseline)
```

## Deviations

- Acceptance criterion text referenced `topology_routing` knob; PR 5 (ADR-0026) renamed
  it to `shape_routing` after the substance audit. Verdict table here uses the
  current name. The baseline JSON/Markdown files keep the pre-rename name as a
  frozen historical artefact; this is documented in
  `FINDINGS-pre-stage-4-ablation.md`.

- PRD-0025 originally listed 3 PRs in the rollout; the actual landing was 4
  (the warmup methodology / firing scenarios needed a fourth PR to give every knob
  a verdict, captured by ADR-0025). PRD-0025 Execution Plan updated to reflect this.

## Shortcut Audit

- [x] No runtime path uses mocks/stubs where real engine integration was required
- [x] No forbidden imports introduced
- [x] No acceptance criteria skipped

## Substance Audit (ADR-0027)

- [x] Implementation matches what names imply — no inherited vocabulary from the
      deprecated sematryx-api codebase without an explicit port/defer/drop decision
      recorded in the Engine vs Legacy-API Registry in
      `docs/process/ADOPTION_GATE.md`. The harness uses `shape_routing` (post-rename)
      and the firing scenario was renamed `shape_routing_firing_current` to drop the
      `topology_` prefix. The remaining inherited terms (`physarum`, `tunneling`)
      appear only in docstrings explaining the audit and the legacy provenance, and
      are recorded in the registry.
- [x] Doc claims about behavior have a behavioral test or ablation verdict. The
      harness *is* the behavioral verification surface — its v2 baseline gives every
      knob a verdict. The `shape_routing` "feature helps" verdict (Δ=+71%, p<0.001)
      is direct evidence; the `memory_override` "rank shift only" verdict is the
      cautionary finding that prevented overclaiming.
- [x] PRD-0025 acceptance criteria are a mix of structural (artifact presence) and
      behavioral (byte-identity test, ablation verdicts). The behavioral criteria
      dominate, so the PRD's Acceptance Shape would mark this feature
      behavioral-verified. (PRD-0025 predates the Acceptance Shape requirement;
      retrofitted here.)
