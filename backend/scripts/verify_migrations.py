#!/usr/bin/env python3
"""Validate Alembic migrations against a disposable or CI database."""
from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AlembicCommand:
    label: str
    args: list[str]


def run(command: AlembicCommand) -> None:
    printable = " ".join(["alembic", *command.args])
    print(f"▶ {command.label}: {printable}")
    subprocess.run(["alembic", *command.args], cwd=BACKEND_ROOT, check=True)


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
    args = parse_args()
    for command in build_plan(roundtrip=args.roundtrip):
        run(command)
    print("✅ alembic migrations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
