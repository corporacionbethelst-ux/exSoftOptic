#!/usr/bin/env python3
"""Preflight checks before installing dependencies or running backend tests."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
RUNTIME_REQUIREMENTS = BACKEND_ROOT / "requirements.txt"
DEV_REQUIREMENTS = BACKEND_ROOT / "requirements-dev.txt"
CRITICAL_REQUIREMENTS = {
    "fastapi": "FastAPI application runtime",
    "sqlalchemy": "SQLAlchemy ORM",
    "asyncpg": "PostgreSQL async driver",
    "alembic": "Database migrations",
    "httpx": "Async API test client",
    "pytest": "Test runner",
    "pytest-asyncio": "Async test support",
}
REQUIRED_FILES = [
    BACKEND_ROOT / "alembic.ini",
    BACKEND_ROOT / "tests" / "conftest.py",
    REPO_ROOT / "docker-compose.yml",
    REPO_ROOT / "docker-compose.test.yml",
    BACKEND_ROOT / ".env.test.example",
    REPO_ROOT / ".github" / "workflows" / "backend-ci.yml",
]
RECOMMENDED_ENV_VARS = ["SECRET_KEY", "DATABASE_URL", "REDIS_URL", "ENVIRONMENT"]


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    blocking: bool = False


def _normalize_requirement(line: str) -> str:
    return line.strip().lower().split("==", maxsplit=1)[0].split(">=", maxsplit=1)[0].split("[", maxsplit=1)[0]


def _load_requirement_names() -> set[str]:
    names: set[str] = set()
    for path in [RUNTIME_REQUIREMENTS, DEV_REQUIREMENTS]:
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-r "):
                continue
            names.add(_normalize_requirement(stripped))
    return names


def check_python_version() -> CheckResult:
    version = sys.version_info
    ok = version >= (3, 11)
    return CheckResult("python-version", ok, f"Python {version.major}.{version.minor}.{version.micro}", blocking=not ok)


def check_virtualenv() -> CheckResult:
    active = bool(os.environ.get("VIRTUAL_ENV")) or sys.prefix != sys.base_prefix
    return CheckResult("virtualenv", active, "active virtualenv detected" if active else "no active virtualenv detected")


def check_required_files() -> CheckResult:
    missing = [str(path.relative_to(REPO_ROOT)) for path in REQUIRED_FILES if not path.exists()]
    return CheckResult("required-files", not missing, "all required files exist" if not missing else f"missing: {', '.join(missing)}", blocking=bool(missing))


def check_requirements() -> list[CheckResult]:
    names = _load_requirement_names()
    results = []
    for package, reason in sorted(CRITICAL_REQUIREMENTS.items()):
        ok = package in names
        results.append(CheckResult(f"requirement:{package}", ok, reason if ok else f"missing requirement for {reason}", blocking=not ok))
    return results


def check_environment() -> CheckResult:
    missing = [name for name in RECOMMENDED_ENV_VARS if not os.environ.get(name)]
    return CheckResult("environment", not missing, "recommended env vars present" if not missing else f"unset before integration tests: {', '.join(missing)}")


def run_checks() -> list[CheckResult]:
    results = [check_python_version(), check_virtualenv(), check_required_files(), check_environment()]
    results.extend(check_requirements())
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as blockers.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = run_checks()
    for result in results:
        status = "OK" if result.ok else ("BLOCKER" if result.blocking else "WARN")
        print(f"[{status}] {result.name}: {result.detail}")
    blockers = [result for result in results if result.blocking and not result.ok]
    warnings = [result for result in results if not result.blocking and not result.ok]
    if blockers or (args.strict and warnings):
        print(f"Preflight failed: {len(blockers)} blocker(s), {len(warnings)} warning(s)")
        return 1
    print(f"Preflight passed: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
