#!/usr/bin/env python3
"""Report GET endpoints that likely need explicit pagination limits."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

ENDPOINTS_DIR = Path("app/api/v1/endpoints")


@dataclass(frozen=True)
class PaginationFinding:
    file: str
    function: str
    line: int
    reason: str


def find_unpaginated_gets(endpoints_dir: Path = ENDPOINTS_DIR) -> list[PaginationFinding]:
    findings: list[PaginationFinding] = []
    for path in sorted(endpoints_dir.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            if not _is_get_endpoint(node):
                continue
            if _has_list_response(node) and not _has_limit_parameter(node):
                findings.append(
                    PaginationFinding(
                        file=str(path),
                        function=node.name,
                        line=node.lineno,
                        reason="GET endpoint returns list-like response without explicit limit parameter",
                    )
                )
    return findings


def _is_get_endpoint(node: ast.AsyncFunctionDef | ast.FunctionDef) -> bool:
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "get":
            return True
    return False


def _has_list_response(node: ast.AsyncFunctionDef | ast.FunctionDef) -> bool:
    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        for keyword in decorator.keywords:
            if keyword.arg == "response_model" and isinstance(keyword.value, ast.Subscript):
                if isinstance(keyword.value.value, ast.Name) and keyword.value.value.id in {"list", "List"}:
                    return True
    return False


def _has_limit_parameter(node: ast.AsyncFunctionDef | ast.FunctionDef) -> bool:
    return any(arg.arg in {"limit", "page_size", "per_page"} for arg in node.args.args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit list endpoints for pagination limits")
    parser.add_argument("--endpoints-dir", type=Path, default=ENDPOINTS_DIR)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when findings exist")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = find_unpaginated_gets(args.endpoints_dir)
    for finding in findings:
        print(f"{finding.file}:{finding.line} {finding.function}: {finding.reason}")
    if findings and args.strict:
        print(f"❌ pagination audit found {len(findings)} issue(s)")
        return 1
    print(f"✅ pagination audit completed with {len(findings)} finding(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
