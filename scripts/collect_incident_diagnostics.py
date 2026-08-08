#!/usr/bin/env python3
"""Collect a secret-free diagnostic snapshot for incident triage."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path = ROOT, timeout: int = 10) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout
        )
        return {
            "available": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip()[:20_000],
            "stderr": completed.stderr.strip()[:4_000],
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "error": type(exc).__name__}


def probe(url: str, *, timeout: float = 5.0) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read(64 * 1024).decode("utf-8", errors="replace")
            try:
                payload: Any = json.loads(body)
            except json.JSONDecodeError:
                payload = body[:1000]
            return {
                "status": response.status,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                "body": payload,
            }
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "status": 0,
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "error": type(exc).__name__,
        }


def collect(*, base_url: str, include_docker: bool) -> dict[str, Any]:
    disk = shutil.disk_usage(ROOT)
    payload: dict[str, Any] = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "disk_total_bytes": disk.total,
            "disk_free_bytes": disk.free,
        },
        "release": run(["git", "rev-parse", "HEAD"]),
        "working_tree": run(["git", "status", "--short"]),
        "health": probe(f"{base_url.rstrip('/')}/health"),
        "readiness": probe(f"{base_url.rstrip('/')}/ready"),
    }
    if include_docker:
        payload["docker_compose_ps"] = run(
            ["docker", "compose", "-f", "docker-compose.production.yml", "ps", "--format", "json"]
        )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=Path("artifacts/diagnostics.json"))
    parser.add_argument("--without-docker", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = collect(base_url=args.base_url, include_docker=not args.without_docker)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅ diagnóstico guardado en {args.output}")
    print("Revise el archivo antes de adjuntarlo; no se recolectan variables de entorno ni logs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
