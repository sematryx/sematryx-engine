from __future__ import annotations

import subprocess
from pathlib import Path

REQUIRED_FILES = [
    Path("docs/architecture/SYSTEM_OVERVIEW.md"),
    Path("docs/process/DEFINITION_OF_DONE.md"),
    Path("docs/process/DEVELOPMENT_WORKFLOW.md"),
    Path("docs/process/INCIDENT_RESPONSE.md"),
    Path("docs/process/OWNERSHIP.md"),
    Path("docs/process/RELEASE_CHECKLIST.md"),
    Path("docs/architecture/decisions/ADR-template.md"),
    Path("docs/architecture/decisions/README.md"),
    Path("docs/prd/PRD-template.md"),
    Path("docs/process/verification/IMPLEMENTATION_VERIFICATION_TEMPLATE.md"),
    Path("docs/planning/ACTIVE_PLAN.md"),
    Path("docs/project_management/CHANGELOG.md"),
    Path("docs/project_management/INTEGRATION_DEBT.md"),
]


def _changed_files() -> list[str]:
    commands = [
        ["git", "diff", "--name-only", "origin/main...HEAD"],  # committed branch delta
        ["git", "diff", "--name-only", "HEAD~1...HEAD"],  # fallback for early repo state
        ["git", "diff", "--name-only"],  # unstaged changes
        ["git", "diff", "--name-only", "--cached"],  # staged changes
        ["git", "ls-files", "--others", "--exclude-standard"],  # untracked files
    ]
    changed: set[str] = set()
    for cmd in commands:
        try:
            output = subprocess.check_output(
                cmd, text=True, stderr=subprocess.DEVNULL
            ).strip()
            if not output:
                continue
            for line in output.splitlines():
                if line.strip():
                    changed.add(line.strip())
        except Exception:
            continue
    return sorted(changed)


def main() -> int:
    errors: list[str] = []

    for required in REQUIRED_FILES:
        if not required.exists():
            errors.append(f"Missing required governance file: {required}")

    changed = _changed_files()
    changed_set = set(changed)
    architecture_changed = any(
        p.startswith("src/sematryx_engine/engine/")
        or p.startswith("src/sematryx_engine/solvers/")
        for p in changed
    )
    engine_or_learning_changed = any(
        p.startswith("src/sematryx_engine/engine/")
        or p.startswith("src/sematryx_engine/learning/")
        for p in changed
    )
    src_changed = any(p.startswith("src/sematryx_engine/") for p in changed)

    tests_changed = any(p.startswith("tests/") for p in changed)
    integration_tests_changed = any(p.startswith("tests/integration/") for p in changed)
    prd_changed = any(
        p.startswith("docs/prd/") and p != "docs/prd/PRD-template.md"
        for p in changed
    )
    verification_changed = any(
        p.startswith("docs/process/verification/")
        and p != "docs/process/verification/IMPLEMENTATION_VERIFICATION_TEMPLATE.md"
        for p in changed
    )
    adr_changed = any(
        p.startswith("docs/architecture/decisions/") and p != "docs/architecture/decisions/README.md"
        for p in changed
    )
    diagram_changed = "docs/architecture/SYSTEM_OVERVIEW.md" in changed_set
    active_plan_changed = "docs/planning/ACTIVE_PLAN.md" in changed_set
    changelog_changed = "docs/project_management/CHANGELOG.md" in changed_set
    debt_changed = "docs/project_management/INTEGRATION_DEBT.md" in changed_set

    if architecture_changed and not adr_changed:
        errors.append(
            "Architecture-related code changed, but no ADR file was updated/added under "
            "docs/architecture/decisions/."
        )
    if architecture_changed and not diagram_changed:
        errors.append(
            "Architecture-related code changed, but docs/architecture/SYSTEM_OVERVIEW.md "
            "was not updated."
        )

    code_changed = src_changed
    if code_changed and not tests_changed:
        errors.append("Code changed under src/, but no tests were updated under tests/.")
    if engine_or_learning_changed and not integration_tests_changed:
        errors.append(
            "Engine/Learning code changed, but no integration test was updated under "
            "tests/integration/."
        )
    if code_changed and not prd_changed:
        errors.append("Code changed under src/, but no PRD was updated/added under docs/prd/.")
    if code_changed and not verification_changed:
        errors.append(
            "Code changed under src/, but no verification report was updated/added under "
            "docs/process/verification/."
        )
    if code_changed and not active_plan_changed:
        errors.append(
            "Code changed under src/, but docs/planning/ACTIVE_PLAN.md was not updated."
        )
    if code_changed and not changelog_changed:
        errors.append(
            "Code changed under src/, but docs/project_management/CHANGELOG.md was not updated."
        )
    if code_changed and not debt_changed:
        errors.append(
            "Code changed under src/, but docs/project_management/INTEGRATION_DEBT.md was not updated."
        )

    if "README.md" not in changed_set and code_changed:
        errors.append("Code changed under src/, but README.md was not updated.")

    # PRD completion quality gate
    for path in changed:
        if not path.startswith("docs/prd/") or path == "docs/prd/PRD-template.md":
            continue
        content = Path(path).read_text(encoding="utf-8")
        if "- [ ]" in content:
            errors.append(f"PRD has unchecked checklist items: {path}")

    # Verification report structure gate
    for path in changed:
        if not path.startswith("docs/process/verification/") or path.endswith("IMPLEMENTATION_VERIFICATION_TEMPLATE.md"):
            continue
        content = Path(path).read_text(encoding="utf-8")
        required_tokens = [
            "PRD:",
            "## Planned vs Implemented",
            "## Commands Run",
            "## Shortcut Audit",
        ]
        for token in required_tokens:
            if token not in content:
                errors.append(f"Verification report missing '{token}': {path}")

    if errors:
        print("Policy checks failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Policy checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
