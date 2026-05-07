from __future__ import annotations

import subprocess
from pathlib import Path

REQUIRED_FILES = [
    Path("docs/process/DEFINITION_OF_DONE.md"),
    Path("docs/process/DEVELOPMENT_WORKFLOW.md"),
    Path("docs/architecture/decisions/ADR-template.md"),
    Path("docs/architecture/decisions/README.md"),
    Path("docs/prd/PRD-template.md"),
]


def _changed_files() -> list[str]:
    commands = [
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        ["git", "diff", "--name-only", "HEAD~1...HEAD"],
        ["git", "diff", "--name-only"],
    ]
    for cmd in commands:
        try:
            output = subprocess.check_output(cmd, text=True).strip()
            if output:
                return output.splitlines()
        except Exception:
            continue
    return []


def main() -> int:
    errors: list[str] = []

    for required in REQUIRED_FILES:
        if not required.exists():
            errors.append(f"Missing required governance file: {required}")

    changed = _changed_files()
    changed_set = set(changed)
    architecture_changed = any(
        p.startswith("src/sematryx_engine/engine/") or p.startswith("src/sematryx_engine/solvers/")
        for p in changed
    )

    tests_changed = any(p.startswith("tests/") for p in changed)
    adr_changed = any(
        p.startswith("docs/architecture/decisions/") and p != "docs/architecture/decisions/README.md"
        for p in changed
    )

    if architecture_changed and not adr_changed:
        errors.append(
            "Architecture-related code changed, but no ADR file was updated/added under "
            "docs/architecture/decisions/."
        )

    code_changed = any(p.startswith("src/sematryx_engine/") for p in changed)
    if code_changed and not tests_changed:
        errors.append("Code changed under src/, but no tests were updated under tests/.")

    if "README.md" not in changed_set and code_changed:
        errors.append("Code changed under src/, but README.md was not updated.")

    if errors:
        print("Policy checks failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Policy checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
