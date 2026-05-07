# Incident Response

## Trigger Examples

- Strategy quality regression over rolling windows
- Repeated policy gate failures
- Unexpected selection drift or unstable pass/fail behavior

## Procedure

1. Freeze policy changes and keep last known good policy active.
2. Collect evidence: test outputs, benchmark deltas, recent PRs.
3. Run anomaly analysis and produce remediation proposal.
4. Validate proposal through deterministic gates.
5. Roll forward or roll back with documented rationale.
