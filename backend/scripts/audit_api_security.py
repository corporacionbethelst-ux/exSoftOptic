#!/usr/bin/env python3
"""Audit FastAPI endpoint modules for explicit auth/permission guards."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENDPOINTS_ROOT = BACKEND_ROOT / "app" / "api" / "v1" / "endpoints"
ROUTE_PATTERN = re.compile(r"@router\.(get|post|put|patch|delete)\(")
SECURITY_MARKERS = ("require_permissions", "require_role", "get_current_user", "get_current_active_user", "Depends(security)")
PUBLIC_ENDPOINT_ALLOWLIST = {
    ("auth.py", "/login"),
    ("auth.py", "/refresh"),
    ("auth.py", "/forgot-password"),
    ("auth.py", "/reset-password"),
    ("observabilidad.py", "/readiness"),
}


@dataclass(frozen=True)
class EndpointFinding:
    file: str
    line: int
    route: str
    reason: str


def route_path(decorator_line: str) -> str:
    match = re.search(r'\("([^"]*)"', decorator_line)
    return match.group(1) if match else "<unknown>"


def route_block(lines: list[str], start_index: int) -> str:
    block = [lines[start_index]]
    for line in lines[start_index + 1 :]:
        if ROUTE_PATTERN.search(line):
            break
        block.append(line)
    return "".join(block)


def audit_file(path: Path) -> list[EndpointFinding]:
    findings: list[EndpointFinding] = []
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if not ROUTE_PATTERN.search(line):
            continue
        route = route_path(line)
        if (path.name, route) in PUBLIC_ENDPOINT_ALLOWLIST:
            continue
        block = route_block(lines, index)
        if not any(marker in block for marker in SECURITY_MARKERS):
            findings.append(
                EndpointFinding(
                    file=str(path.relative_to(BACKEND_ROOT)),
                    line=index + 1,
                    route=route,
                    reason="missing explicit auth or permission dependency",
                )
            )
    return findings


def audit_endpoints() -> list[EndpointFinding]:
    findings: list[EndpointFinding] = []
    for path in sorted(ENDPOINTS_ROOT.glob("*.py")):
        if path.name == "__init__.py":
            continue
        findings.extend(audit_file(path))
    return findings


def main() -> int:
    findings = audit_endpoints()
    if findings:
        for finding in findings:
            print(f"❌ {finding.file}:{finding.line} {finding.route} - {finding.reason}")
        return 1
    print("✅ API endpoint security audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
