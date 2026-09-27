#!/usr/bin/env python3
"""Dependency-free HTTP capacity smoke test with enforceable SLO thresholds."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class RequestResult:
    status_code: int
    latency_ms: float
    error: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class LoadSummary:
    total: int
    success: int
    failed: int
    p95_latency_ms: float
    average_latency_ms: float
    p50_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    duration_seconds: float = 0.0
    requests_per_second: float = 0.0
    status_codes: dict[str, int] | None = None
    errors: dict[str, int] | None = None


@dataclass(frozen=True)
class LoadPlan:
    urls: list[str]
    requests: int = 50
    concurrency: int = 5
    warmup_requests: int = 5
    timeout_seconds: float = 5.0
    max_failure_rate: float = 0.01
    max_p95_ms: float = 1000.0
    max_p99_ms: float = 2000.0
    min_requests_per_second: float = 0.0


def run_request(
    url: str,
    *,
    timeout_seconds: float,
    headers: dict[str, str] | None = None,
) -> RequestResult:
    started = time.perf_counter()
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response.read()
            return RequestResult(
                status_code=response.getcode(),
                latency_ms=(time.perf_counter() - started) * 1000,
                url=url,
            )
    except urllib.error.HTTPError as exc:
        return RequestResult(
            status_code=exc.code,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=f"HTTP {exc.code}",
            url=url,
        )
    except (urllib.error.URLError, TimeoutError) as exc:
        return RequestResult(
            status_code=0,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=type(exc).__name__,
            url=url,
        )


def summarize(results: list[RequestResult], *, duration_seconds: float = 0.0) -> LoadSummary:
    latencies = [result.latency_ms for result in results]
    success = sum(1 for result in results if 200 <= result.status_code < 400)
    failed = len(results) - success
    duration = max(duration_seconds, 0.0)
    return LoadSummary(
        total=len(results),
        success=success,
        failed=failed,
        p50_latency_ms=round(percentile(latencies, 50), 3),
        p95_latency_ms=round(percentile(latencies, 95), 3),
        p99_latency_ms=round(percentile(latencies, 99), 3),
        average_latency_ms=round(statistics.fmean(latencies), 3) if latencies else 0.0,
        duration_seconds=round(duration, 3),
        requests_per_second=round(len(results) / duration, 3) if duration > 0 else 0.0,
        status_codes=dict(sorted(Counter(str(result.status_code) for result in results).items())),
        errors=dict(sorted(Counter(result.error for result in results if result.error).items())),
    )


def percentile(values: list[float], percentile_value: int) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = max(1, int((percentile_value / 100) * len(ordered) + 0.999999))
    return ordered[min(rank - 1, len(ordered) - 1)]


def execute_plan(
    plan: LoadPlan,
    *,
    headers: dict[str, str] | None = None,
    requester: Callable[..., RequestResult] = run_request,
) -> LoadSummary:
    for index in range(plan.warmup_requests):
        requester(
            plan.urls[index % len(plan.urls)],
            timeout_seconds=plan.timeout_seconds,
            headers=headers,
        )

    started = time.perf_counter()
    results: list[RequestResult] = []
    with ThreadPoolExecutor(max_workers=plan.concurrency) as executor:
        futures = [
            executor.submit(
                requester,
                plan.urls[index % len(plan.urls)],
                timeout_seconds=plan.timeout_seconds,
                headers=headers,
            )
            for index in range(plan.requests)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    return summarize(results, duration_seconds=time.perf_counter() - started)


def evaluate(summary: LoadSummary, plan: LoadPlan) -> list[str]:
    failure_rate = summary.failed / summary.total if summary.total else 1.0
    failures: list[str] = []
    if failure_rate > plan.max_failure_rate:
        failures.append(f"failure_rate {failure_rate:.4f} > {plan.max_failure_rate:.4f}")
    if summary.p95_latency_ms > plan.max_p95_ms:
        failures.append(f"p95_ms {summary.p95_latency_ms} > {plan.max_p95_ms}")
    if summary.p99_latency_ms > plan.max_p99_ms:
        failures.append(f"p99_ms {summary.p99_latency_ms} > {plan.max_p99_ms}")
    if summary.requests_per_second < plan.min_requests_per_second:
        failures.append(
            f"requests_per_second {summary.requests_per_second} < {plan.min_requests_per_second}"
        )
    return failures


def load_plan(path: Path | None, args: argparse.Namespace) -> LoadPlan:
    data: dict[str, object] = {}
    if path:
        data = json.loads(path.read_text(encoding="utf-8"))
    overrides = {
        key: value
        for key, value in {
            "urls": args.urls,
            "requests": args.requests,
            "concurrency": args.concurrency,
            "warmup_requests": args.warmup_requests,
            "timeout_seconds": args.timeout_seconds,
            "max_failure_rate": args.max_failure_rate,
            "max_p95_ms": args.max_p95_ms,
            "max_p99_ms": args.max_p99_ms,
            "min_requests_per_second": args.min_requests_per_second,
        }.items()
        if value is not None
    }
    data.update(overrides)
    data.setdefault("urls", ["http://localhost:8000/health"])
    return LoadPlan(**data)  # type: ignore[arg-type]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slo-file", type=Path)
    parser.add_argument("--url", dest="urls", action="append")
    parser.add_argument("--requests", type=int)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--warmup-requests", type=int)
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--max-failure-rate", type=float)
    parser.add_argument("--max-p95-ms", type=float)
    parser.add_argument("--max-p99-ms", type=float)
    parser.add_argument("--min-requests-per-second", type=float)
    parser.add_argument("--header", action="append", default=[])
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = load_plan(args.slo_file, args)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        print(f"Configuración de carga inválida: {exc}", file=sys.stderr)
        return 2
    if (
        not plan.urls
        or plan.requests < 1
        or plan.concurrency < 1
        or plan.warmup_requests < 0
        or plan.concurrency > plan.requests
    ):
        print("Plan inválido: revise URLs, requests, concurrency y warmup", file=sys.stderr)
        return 2
    headers: dict[str, str] = {}
    for raw_header in args.header:
        if ":" not in raw_header:
            print(f"Header inválido: {raw_header}", file=sys.stderr)
            return 2
        key, value = raw_header.split(":", 1)
        headers[key.strip()] = value.strip()

    summary = execute_plan(plan, headers=headers)
    payload = {"plan": asdict(plan), "summary": asdict(summary)}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    failures = evaluate(summary, plan)
    if failures:
        for failure in failures:
            print(f"❌ {failure}", file=sys.stderr)
        return 1
    print("✅ load smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
