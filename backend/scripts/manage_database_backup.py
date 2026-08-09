#!/usr/bin/env python3
"""Create and restore PostgreSQL backups for operational recovery."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit


@dataclass(frozen=True)
class BackupCommand:
    args: list[str]
    env: dict[str, str]


def postgres_cli_connection(database_url: str) -> tuple[str, dict[str, str]]:
    """Return a libpq URL without password in argv and password in process env."""
    normalized = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    parsed = urlsplit(normalized)
    if parsed.scheme not in {"postgresql", "postgres"}:
        raise ValueError("DATABASE_URL debe ser PostgreSQL")
    hostname = parsed.hostname or ""
    host = f"[{hostname}]" if ":" in hostname else hostname
    credentials = quote(unquote(parsed.username or ""), safe="")
    netloc = f"{credentials}@{host}" if credentials else host
    if parsed.port:
        netloc += f":{parsed.port}"
    safe_url = urlunsplit(("postgresql", netloc, parsed.path, parsed.query, ""))
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = unquote(parsed.password)
    return safe_url, env


def build_backup_command(*, database_url: str, output: Path) -> BackupCommand:
    safe_url, env = postgres_cli_connection(database_url)
    return BackupCommand(
        args=[
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(output),
            safe_url,
        ],
        env=env,
    )


def build_restore_command(*, database_url: str, input_file: Path, clean: bool) -> BackupCommand:
    safe_url, env = postgres_cli_connection(database_url)
    args = ["pg_restore", "--no-owner", "--no-privileges", "--dbname", safe_url]
    if clean:
        args.extend(["--clean", "--if-exists"])
    args.append(str(input_file))
    return BackupCommand(args=args, env=env)


def checksum_path(backup: Path) -> Path:
    return backup.with_suffix(backup.suffix + ".sha256")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksum(backup: Path) -> Path:
    destination = checksum_path(backup)
    destination.write_text(f"{sha256_file(backup)}  {backup.name}\n", encoding="utf-8")
    return destination


def verify_checksum(backup: Path, *, required: bool) -> bool:
    manifest = checksum_path(backup)
    if not manifest.exists():
        if required:
            print(f"Checksum no encontrado: {manifest}", file=sys.stderr)
            return False
        print(f"ADVERTENCIA: checksum no encontrado para {backup}", file=sys.stderr)
        return True
    fields = manifest.read_text(encoding="utf-8").split()
    if not fields or len(fields[0]) != 64:
        print(f"Manifest de checksum inválido: {manifest}", file=sys.stderr)
        return False
    expected = fields[0]
    actual = sha256_file(backup)
    if not hmac.compare_digest(expected, actual):
        print(f"Checksum inválido para {backup}", file=sys.stderr)
        return False
    print(f"✅ checksum SHA-256 válido: {backup}")
    return True


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
    restore.add_argument("--require-checksum", action="store_true")
    restore.add_argument("--dry-run", action="store_true")

    verify = subparsers.add_parser("verify", help="Verify a backup SHA-256 manifest")
    verify.add_argument("--input", type=Path, required=True)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.action != "verify" and not args.database_url:
        print("DATABASE_URL es obligatorio", file=sys.stderr)
        return 2
    if args.action == "backup":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output = args.output or default_backup_path(args.output_dir)
        try:
            command = build_backup_command(database_url=args.database_url, output=output)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        result = run_command(command, dry_run=args.dry_run)
        if result == 0 and not args.dry_run:
            manifest = write_checksum(output)
            print(f"✅ backup creado: {output}")
            print(f"✅ checksum creado: {manifest}")
        return result
    if args.action == "verify":
        if not args.input.exists():
            print(f"Backup no encontrado: {args.input}", file=sys.stderr)
            return 2
        return 0 if verify_checksum(args.input, required=True) else 1
    if not args.input.exists() and not args.dry_run:
        print(f"Backup no encontrado: {args.input}", file=sys.stderr)
        return 2
    if not args.dry_run and not verify_checksum(args.input, required=args.require_checksum):
        return 1
    try:
        command = build_restore_command(
            database_url=args.database_url, input_file=args.input, clean=args.clean
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return run_command(command, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
