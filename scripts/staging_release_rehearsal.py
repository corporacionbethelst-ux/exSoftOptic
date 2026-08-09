#!/usr/bin/env python3
"""Create or execute a reproducible staging release rehearsal.

The default mode only writes the release plan. Execution must be explicitly
enabled with ``--execute`` so reviewing the exact commands remains mandatory.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_plan(path: Path) -> dict:
    plan = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "environment",
        "compose_file",
        "health_path",
        "readiness_path",
        "readiness_timeout_seconds",
        "required_evidence",
    }
    missing = sorted(required - plan.keys())
    if missing:
        raise ValueError(f"release plan missing fields: {', '.join(missing)}")
    if plan["environment"] != "staging":
        raise ValueError("release rehearsals may only target staging")
    if not isinstance(plan["required_evidence"], list) or not plan["required_evidence"]:
        raise ValueError("required_evidence must be a non-empty list")
    return plan


def release_commands(plan: dict, env_file: str, base_url: str) -> list[list[str]]:
    compose = [
        "docker", "compose", "--env-file", env_file,
        "-f", plan["compose_file"], "-p", "exsoftoptic-staging",
    ]
    return [
        [sys.executable, "backend/scripts/validate_runtime_config.py", "--env-file", env_file,
         "--environment", "production", "--strict"],
        [*compose, "config", "--quiet"],
        [*compose, "pull", "--ignore-buildable"],
        [*compose, "build", "--pull"],
        [*compose, "--profile", "migration", "run", "--rm", "migration-job"],
        [*compose, "up", "-d", "--remove-orphans"],
        [sys.executable, "backend/scripts/load_smoke.py",
         "--slo-file", "ops/performance/staging-slo.json",
         "--url", base_url.rstrip("/") + plan["health_path"],
         "--url", base_url.rstrip("/") + plan["readiness_path"],
         "--output-json", "artifacts/staging-load-smoke.json"],
        [sys.executable, "e2e/browser_smoke.py", "--base-url", base_url],
    ]


def check_image_references(env_file: Path) -> None:
    values: dict[str, str] = {}
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value.strip()
    for key in ("BACKEND_IMAGE", "FRONTEND_IMAGE"):
        value = values.get(key, "")
        if not value or value.endswith(":latest") or value.endswith(":production"):
            raise ValueError(f"{key} must use an immutable release tag or digest")


def wait_for_endpoint(url: str, timeout: int) -> None:
    deadline = time.monotonic() + timeout
    last_error = "not attempted"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if 200 <= response.status < 300:
                    return
                last_error = f"HTTP {response.status}"
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"endpoint did not become ready: {url} ({last_error})")


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True, env=os.environ.copy())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="ops/release/staging-plan.json")
    parser.add_argument("--env-file", default=".env.staging")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--output", default="artifacts/staging-release-plan.json")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--skip-browser", action="store_true")
    args = parser.parse_args()

    try:
        plan = load_plan(ROOT / args.plan)
        commands = release_commands(plan, args.env_file, args.base_url)
        if args.skip_browser:
            commands = commands[:-1]
        record = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "environment": "staging",
            "mode": "execute" if args.execute else "plan",
            "base_url": args.base_url,
            "commands": commands,
            "required_evidence": plan["required_evidence"],
            "status": "planned",
        }
        output = ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"Release record: {output}")
        for command in commands:
            print("+", " ".join(command))
        if not args.execute:
            return 0

        check_image_references(ROOT / args.env_file)
        for index, command in enumerate(commands):
            if index == 6:
                timeout = int(plan["readiness_timeout_seconds"])
                wait_for_endpoint(args.base_url.rstrip("/") + plan["health_path"], timeout)
                wait_for_endpoint(args.base_url.rstrip("/") + plan["readiness_path"], timeout)
            run(command)
        record["status"] = "technical-checks-passed"
        record["completed_at"] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"release rehearsal failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
