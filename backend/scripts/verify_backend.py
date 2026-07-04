#!/usr/bin/env python3
"""Run backend verification checks with actionable dependency diagnostics."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
PYTHON_DIRS = (BACKEND_ROOT / "app", BACKEND_ROOT / "tests", BACKEND_ROOT / "alembic")
REQUIRED_MODULES = {
    "fastapi": "FastAPI application runtime",
    "sqlalchemy": "SQLAlchemy ORM and async sessions",
    "pydantic": "Pydantic schemas and settings",
    "asyncpg": "PostgreSQL async test/runtime driver",
    "httpx": "Async API test client",
    "pytest": "Automated test runner",
}


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def _status(result: CheckResult) -> str:
    icon = "✅" if result.ok else "❌"
    return f"{icon} {result.name}: {result.detail}"


def check_required_modules() -> CheckResult:
    missing = [module for module in REQUIRED_MODULES if importlib.util.find_spec(module) is None]
    if not missing:
        return CheckResult("dependencies", True, "required Python modules are importable")

    details = ", ".join(f"{module} ({REQUIRED_MODULES[module]})" for module in missing)
    return CheckResult(
        "dependencies",
        False,
        "missing modules: "
        f"{details}. Install them with `cd backend && python -m pip install -r requirements-dev.txt`.",
    )


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for base in PYTHON_DIRS:
        if not base.exists():
            continue
        files.extend(path for path in base.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(files)


def check_python_syntax() -> CheckResult:
    checked = 0
    for path in iter_python_files():
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            location = f"{path.relative_to(REPO_ROOT)}:{exc.lineno}:{exc.offset}"
            return CheckResult("syntax", False, f"{location} {exc.msg}")
        checked += 1
    return CheckResult("syntax", True, f"parsed {checked} Python files")


def run_pytest(extra_args: list[str]) -> CheckResult:
    command = [sys.executable, "-m", "pytest", *extra_args]
    completed = subprocess.run(command, cwd=BACKEND_ROOT)
    if completed.returncode == 0:
        return CheckResult("pytest", True, "test suite passed")
    return CheckResult("pytest", False, f"test suite exited with code {completed.returncode}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Only validate dependencies and Python syntax; do not execute pytest.",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded to pytest after `--`, default: -q.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pytest_args = args.pytest_args
    if pytest_args and pytest_args[0] == "--":
        pytest_args = pytest_args[1:]
    if not pytest_args:
        pytest_args = ["-q"]

    results = [check_required_modules(), check_python_syntax()]
    for result in results:
        print(_status(result))

    if not all(result.ok for result in results):
        return 2

    if args.skip_pytest:
        print("⚠️ pytest: skipped by --skip-pytest")
        return 0

    pytest_result = run_pytest(pytest_args)
    print(_status(pytest_result))
    return 0 if pytest_result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
