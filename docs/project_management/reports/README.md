# Benchmark reports

Generated snapshots are optional local artifacts. Typical workflow:

```bash
make report-benchmark
```

To write files:

```bash
.venv311/bin/python scripts/generate_benchmark_trend_report.py \
  --json-out docs/project_management/reports/benchmark_snapshot.json \
  --md-out docs/project_management/reports/benchmark_snapshot.md
```

Add generated `benchmark_snapshot.*` files to `.gitignore` if you do not want them tracked.
