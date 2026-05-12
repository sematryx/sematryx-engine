.PHONY: install lint typecheck test smoke benchmark report-benchmark ablation ablation-full policy all

install:
	.venv311/bin/python -m pip install -e ".[dev]"

lint:
	.venv311/bin/python -m ruff check src tests scripts

typecheck:
	.venv311/bin/python -m mypy src

test:
	.venv311/bin/python -m pytest tests/unit tests/smoke

smoke:
	.venv311/bin/python -m pytest tests/smoke

benchmark:
	.venv311/bin/python -m pytest tests/performance tests/integration/test_stage3_discrete_validation_scenarios.py tests/integration/test_stage3_discrete_cold_warm_selection.py

report-benchmark:
	.venv311/bin/python scripts/generate_benchmark_trend_report.py

ablation:
	.venv311/bin/python scripts/generate_ablation_report.py --mode light

ablation-full:
	.venv311/bin/python scripts/generate_ablation_report.py --mode heavy

policy:
	.venv311/bin/python scripts/check_forbidden_imports.py
	.venv311/bin/python scripts/check_policy.py
	.venv311/bin/python scripts/check_release_checklist.py

all: lint typecheck test policy
