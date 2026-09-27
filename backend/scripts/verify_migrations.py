#!/usr/bin/env python3
"""Validate Alembic migrations against a disposable or CI database."""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def load_env_file(path: Path, *, protected_keys: set[str]) -> None:
    """Load simple KEY=VALUE entries without overriding protected variables."""
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key not in protected_keys:
            os.environ[key] = value


def load_test_environment() -> None:
    """Load test DB defaults for Alembic unless caller exported env vars."""
    protected_keys = set(os.environ)
    load_env_file(BACKEND_ROOT / ".env.test", protected_keys=protected_keys)
    load_env_file(BACKEND_ROOT / ".env.test.local", protected_keys=protected_keys)
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://optica_user:optica_password_2026@localhost:55432/optica_test",
    )


def ensure_alembic_available() -> None:
    """Fail fast with an actionable message when Alembic is not installed."""
    try:
        spec = importlib.util.find_spec("alembic.config")
    except ModuleNotFoundError:
        spec = None
    if spec is None:
        raise SystemExit(
            "❌ Alembic is not installed in the active Python environment. "
            "Run `cd backend && python -m pip install -r requirements-dev.txt` and retry."
        )


@dataclass(frozen=True)
class AlembicCommand:
    label: str
    args: list[str]


def run(command: AlembicCommand) -> None:
    invoker = [sys.executable, "-c", "from alembic.config import main; main()"]
    printable = " ".join([sys.executable, "-c", invoker[2], *command.args])
    print(f"▶ {command.label}: {printable}")
    subprocess.run([*invoker, *command.args], cwd=BACKEND_ROOT, check=True)


def build_plan(*, roundtrip: bool) -> list[AlembicCommand]:
    plan = [
        AlembicCommand("ensure single migration head", ["heads"]),
        AlembicCommand("upgrade database to head", ["upgrade", "head"]),
        AlembicCommand("verify current revision", ["current"]),
        AlembicCommand("verify upgrade idempotency", ["upgrade", "head"]),
    ]
    if roundtrip:
        plan.extend(
            [
                AlembicCommand("downgrade disposable database to base", ["downgrade", "base"]),
                AlembicCommand("re-upgrade disposable database to head", ["upgrade", "head"]),
                AlembicCommand("verify current revision after roundtrip", ["current"]),
            ]
        )
    return plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roundtrip",
        action="store_true",
        help="Also downgrade to base and upgrade again. Use only on disposable CI/test databases.",
    )
    return parser.parse_args()


def main() -> int:
    load_test_environment()
    args = parse_args()
    ensure_alembic_available()
    load_test_environment()
    for command in build_plan(roundtrip=args.roundtrip):
        run(command)
    print("✅ alembic migrations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
