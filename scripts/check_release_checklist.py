from __future__ import annotations

from pathlib import Path

CHECKLIST_PATH = Path("docs/process/RELEASE_CHECKLIST.md")
REQUIRED_ITEMS = [
    "`make all` passes",
    "`CI / required-checks` is green (includes `integration-performance`: `pytest tests/integration tests/performance --import-mode=importlib`)",
    "PRD and verification report are complete",
    "ADR updates merged for architecture changes",
    "CHANGELOG updated",
    "INTEGRATION_DEBT updated",
    "Branch protection and required checks enabled",
    "Rollback plan documented in PR",
]


def main() -> int:
    if not CHECKLIST_PATH.exists():
        print(f"Missing release checklist: {CHECKLIST_PATH}")
        return 1

    content = CHECKLIST_PATH.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_ITEMS if item not in content]
    if missing:
        print("Release checklist is missing required items:")
        for item in missing:
            print(f" - {item}")
        return 1

    print("Release checklist structure is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
