from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_PREFIXES = (
    "google.cloud",
    "neo4j",
    "fastapi",
    "uvicorn",
    "mcp",
    "sematryx.platform_services",
)

TARGET_ROOT = Path("src/sematryx_engine")


def _is_forbidden(module_name: str) -> bool:
    return any(
        module_name == prefix or module_name.startswith(prefix + ".")
        for prefix in FORBIDDEN_PREFIXES
    )


def main() -> int:
    violations: list[str] = []
    for path in TARGET_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if _is_forbidden(alias.name):
                        violations.append(f"{path}: forbidden import '{alias.name}'")
            if isinstance(node, ast.ImportFrom) and node.module:
                if _is_forbidden(node.module):
                    violations.append(f"{path}: forbidden import '{node.module}'")

    if violations:
        print("Forbidden imports detected:")
        for violation in violations:
            print(f" - {violation}")
        return 1

    print("No forbidden imports found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
