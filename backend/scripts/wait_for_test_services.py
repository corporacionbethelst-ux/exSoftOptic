#!/usr/bin/env python3
"""Wait for isolated backend test services to accept TCP connections."""

from __future__ import annotations

import argparse
import socket
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceProbe:
    name: str
    host: str
    port: int


DEFAULT_PROBES = [
    ServiceProbe("postgres-test", "127.0.0.1", 55432),
    ServiceProbe("redis-test", "127.0.0.1", 56379),
    ServiceProbe("mongodb-test", "127.0.0.1", 57017),
]


def can_connect(host: str, port: int, timeout_seconds: float = 1.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout_seconds)
        return sock.connect_ex((host, port)) == 0


def wait_for_services(probes: list[ServiceProbe], *, timeout_seconds: float, interval_seconds: float) -> list[str]:
    deadline = time.monotonic() + timeout_seconds
    pending = {probe.name: probe for probe in probes}
    while pending and time.monotonic() < deadline:
        for name, probe in list(pending.items()):
            if can_connect(probe.host, probe.port, timeout_seconds=min(interval_seconds, 1.0)):
                print(f"[OK] {probe.name} accepting TCP on {probe.host}:{probe.port}")
                pending.pop(name)
        if pending:
            time.sleep(interval_seconds)
    return sorted(pending)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--interval-seconds", type=float, default=2.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = wait_for_services(DEFAULT_PROBES, timeout_seconds=args.timeout_seconds, interval_seconds=args.interval_seconds)
    if missing:
        print(f"[BLOCKER] services not ready: {', '.join(missing)}")
        return 1
    print("All isolated backend test services are reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
