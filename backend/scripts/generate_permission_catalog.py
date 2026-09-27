#!/usr/bin/env python3
"""Generate a permission catalog from FastAPI endpoint declarations."""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from pathlib import Path


ENDPOINTS_DIR = Path("app/api/v1/endpoints")
DEFAULT_OUTPUT = Path("../docs/backend-permissions.md")


def collect_permissions(endpoints_dir: Path = ENDPOINTS_DIR) -> dict[str, set[str]]:
    permissions_by_module: dict[str, set[str]] = defaultdict(set)
    for path in sorted(endpoints_dir.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_require_permissions_call(node):
                for permission in _extract_string_list(node):
                    permissions_by_module[permission.split(".")[0]].add(permission)
    return permissions_by_module


def _is_require_permissions_call(node: ast.Call) -> bool:
    return isinstance(node.func, ast.Name) and node.func.id == "require_permissions"


def _extract_string_list(node: ast.Call) -> list[str]:
    if not node.args or not isinstance(node.args[0], ast.List):
        return []
    values: list[str] = []
    for item in node.args[0].elts:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            values.append(item.value)
    return values


def render_markdown(permissions_by_module: dict[str, set[str]]) -> str:
    lines = [
        "# Backend permission catalog",
        "",
        "This catalog is generated from `require_permissions([...])` declarations in `backend/app/api/v1/endpoints`.",
        "",
        "Use it as the baseline for RBAC role templates and access reviews.",
        "",
    ]
    for module in sorted(permissions_by_module):
        lines.append(f"## {module}")
        lines.append("")
        for permission in sorted(permissions_by_module[module]):
            lines.append(f"- `{permission}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate backend permission catalog")
    parser.add_argument("--endpoints-dir", type=Path, default=ENDPOINTS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if output is not up to date")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rendered = render_markdown(collect_permissions(args.endpoints_dir))
    if args.check:
        current = args.output.read_text() if args.output.exists() else ""
        if current != rendered:
            print(f"❌ permission catalog is out of date: {args.output}")
            return 1
        print("✅ permission catalog is up to date")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(f"✅ permission catalog written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
