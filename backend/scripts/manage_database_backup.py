#!/usr/bin/env python3
"""Create and restore PostgreSQL backups for operational recovery."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class BackupCommand:
    args: list[str]
    env: dict[str, str]


def build_backup_command(*, database_url: str, output: Path) -> BackupCommand:
    return BackupCommand(
        args=[
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(output),
            database_url,
        ],
        env=os.environ.copy(),
    )


def build_restore_command(*, database_url: str, input_file: Path, clean: bool) -> BackupCommand:
    args = ["pg_restore", "--no-owner", "--no-privileges", "--dbname", database_url]
    if clean:
        args.extend(["--clean", "--if-exists"])
    args.append(str(input_file))
    return BackupCommand(args=args, env=os.environ.copy())


def default_backup_path(directory: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return directory / f"exsoftoptic-backend-{timestamp}.dump"


def run_command(command: BackupCommand, *, dry_run: bool) -> int:
    printable = " ".join(command.args)
    if dry_run:
        print(printable)
        return 0
    completed = subprocess.run(command.args, env=command.env, check=False)
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup or restore the backend PostgreSQL database")
    subparsers = parser.add_subparsers(dest="action", required=True)

    backup = subparsers.add_parser("backup", help="Create a pg_dump custom-format backup")
    backup.add_argument("--database-url", default=os.getenv("DATABASE_URL", ""))
    backup.add_argument("--output-dir", type=Path, default=Path("./backups"))
    backup.add_argument("--output", type=Path)
    backup.add_argument("--dry-run", action="store_true")

    restore = subparsers.add_parser("restore", help="Restore a pg_dump custom-format backup")
    restore.add_argument("--database-url", default=os.getenv("DATABASE_URL", ""))
    restore.add_argument("--input", type=Path, required=True)
    restore.add_argument("--clean", action="store_true")
    restore.add_argument("--dry-run", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.database_url:
        print("DATABASE_URL es obligatorio", file=sys.stderr)
        return 2
    if args.action == "backup":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output = args.output or default_backup_path(args.output_dir)
        return run_command(build_backup_command(database_url=args.database_url, output=output), dry_run=args.dry_run)
    if not args.input.exists() and not args.dry_run:
        print(f"Backup no encontrado: {args.input}", file=sys.stderr)
        return 2
    return run_command(
        build_restore_command(database_url=args.database_url, input_file=args.input, clean=args.clean),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
