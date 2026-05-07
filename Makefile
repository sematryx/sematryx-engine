.PHONY: install lint typecheck test smoke policy all

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

policy:
	.venv311/bin/python scripts/check_forbidden_imports.py
	.venv311/bin/python scripts/check_policy.py

all: lint typecheck test policy
