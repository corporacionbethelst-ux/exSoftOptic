#!/usr/bin/env python3
"""Small dependency-free HTTP load smoke test for backend endpoints."""

from __future__ import annotations

import argparse
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestResult:
    status_code: int
    latency_ms: float
    error: str | None = None


@dataclass(frozen=True)
class LoadSummary:
    total: int
    success: int
    failed: int
    p95_latency_ms: float
    average_latency_ms: float


def run_request(url: str, *, timeout_seconds: float) -> RequestResult:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            response.read()
            status_code = response.getcode()
            return RequestResult(status_code=status_code, latency_ms=(time.perf_counter() - started) * 1000)
    except urllib.error.HTTPError as exc:
        return RequestResult(status_code=exc.code, latency_ms=(time.perf_counter() - started) * 1000, error=str(exc))
    except urllib.error.URLError as exc:
        return RequestResult(status_code=0, latency_ms=(time.perf_counter() - started) * 1000, error=str(exc))


def summarize(results: list[RequestResult]) -> LoadSummary:
    latencies = [result.latency_ms for result in results]
    p95 = percentile(latencies, 95) if latencies else 0.0
    success = sum(1 for result in results if 200 <= result.status_code < 400)
    failed = len(results) - success
    average = statistics.fmean(latencies) if latencies else 0.0
    return LoadSummary(
        total=len(results),
        success=success,
        failed=failed,
        p95_latency_ms=round(p95, 3),
        average_latency_ms=round(average, 3),
    )


def percentile(values: list[float], percentile_value: int) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round((percentile_value / 100) * len(ordered) + 0.5) - 1))
    return ordered[index]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight load smoke test")
    parser.add_argument("--url", default="http://localhost:8000/health")
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--max-failure-rate", type=float, default=0.01)
    parser.add_argument("--max-p95-ms", type=float, default=1000.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.requests < 1 or args.concurrency < 1:
        print("requests y concurrency deben ser mayores que cero", file=sys.stderr)
        return 2
    results: list[RequestResult] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(run_request, args.url, timeout_seconds=args.timeout_seconds) for _ in range(args.requests)]
        for future in as_completed(futures):
            results.append(future.result())
    summary = summarize(results)
    failure_rate = summary.failed / summary.total if summary.total else 1.0
    print(
        " ".join(
            [
                f"total={summary.total}",
                f"success={summary.success}",
                f"failed={summary.failed}",
                f"failure_rate={failure_rate:.4f}",
                f"avg_ms={summary.average_latency_ms}",
                f"p95_ms={summary.p95_latency_ms}",
            ]
        )
    )
    if failure_rate > args.max_failure_rate:
        print("❌ load smoke failed: failure rate exceeded", file=sys.stderr)
        return 1
    if summary.p95_latency_ms > args.max_p95_ms:
        print("❌ load smoke failed: p95 latency exceeded", file=sys.stderr)
        return 1
    print("✅ load smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
