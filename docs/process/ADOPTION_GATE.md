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
