import time
from collections import defaultdict
from threading import Lock
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RuntimeMetrics:
    """Contadores runtime en memoria para observabilidad operativa ligera."""

    LATENCY_BUCKETS_MS = (
        5.0,
        10.0,
        25.0,
        50.0,
        100.0,
        250.0,
        500.0,
        1000.0,
        2500.0,
        5000.0,
    )

    def __init__(self) -> None:
        self.started_at = time.time()
        self._started_monotonic = time.monotonic()
        self._requests_total = 0
        self._responses_by_status: dict[int, int] = defaultdict(int)
        self._exceptions_total = 0
        self._latency_total_ms = 0.0
        self._responses_by_route: dict[tuple[str, str, int], int] = defaultdict(int)
        self._latency_buckets: dict[float, int] = defaultdict(int)
        self._in_flight = 0
        self._lock = Lock()

    def record_response(self, *, status_code: int, latency_ms: float, method: str | None = None, path: str | None = None) -> None:
        with self._lock:
            self._requests_total += 1
            self._responses_by_status[status_code] += 1
            self._latency_total_ms += latency_ms
            for boundary in self.LATENCY_BUCKETS_MS:
                if latency_ms <= boundary:
                    self._latency_buckets[boundary] += 1
            if method and path:
                self._responses_by_route[(method, path, status_code)] += 1

    def record_exception(self, *, latency_ms: float) -> None:
        with self._lock:
            self._requests_total += 1
            self._exceptions_total += 1
            self._latency_total_ms += latency_ms
            for boundary in self.LATENCY_BUCKETS_MS:
                if latency_ms <= boundary:
                    self._latency_buckets[boundary] += 1

    def request_started(self) -> None:
        with self._lock:
            self._in_flight += 1

    def request_finished(self) -> None:
        with self._lock:
            self._in_flight = max(0, self._in_flight - 1)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            avg_latency = self._latency_total_ms / self._requests_total if self._requests_total else 0.0
            return {
                "started_at_epoch": self.started_at,
                "uptime_seconds": round(time.monotonic() - self._started_monotonic, 3),
                "requests_total": self._requests_total,
                "responses_by_status": {str(status): count for status, count in sorted(self._responses_by_status.items())},
                "exceptions_total": self._exceptions_total,
                "average_latency_ms": round(avg_latency, 3),
                "latency_total_ms": round(self._latency_total_ms, 3),
                "in_flight": self._in_flight,
                "latency_buckets_ms": {
                    str(boundary): self._latency_buckets[boundary]
                    for boundary in self.LATENCY_BUCKETS_MS
                },
                "responses_by_route": [
                    {"method": method, "path": path, "status_code": status, "count": count}
                    for (method, path, status), count in sorted(self._responses_by_route.items())
                ],
            }

    def prometheus_text(self) -> str:
        snapshot = self.snapshot()
        lines = [
            "# HELP exsoftoptic_uptime_seconds Backend process uptime in seconds",
            "# TYPE exsoftoptic_uptime_seconds gauge",
            f"exsoftoptic_uptime_seconds {snapshot['uptime_seconds']}",
            "# HELP exsoftoptic_requests_total Total HTTP requests observed by middleware",
            "# TYPE exsoftoptic_requests_total counter",
            f"exsoftoptic_requests_total {snapshot['requests_total']}",
            "# HELP exsoftoptic_exceptions_total Total unhandled exceptions observed by middleware",
            "# TYPE exsoftoptic_exceptions_total counter",
            f"exsoftoptic_exceptions_total {snapshot['exceptions_total']}",
            "# HELP exsoftoptic_request_latency_average_ms Average request latency in milliseconds",
            "# TYPE exsoftoptic_request_latency_average_ms gauge",
            f"exsoftoptic_request_latency_average_ms {snapshot['average_latency_ms']}",
            "# HELP exsoftoptic_request_latency_total_ms Total accumulated request latency in milliseconds",
            "# TYPE exsoftoptic_request_latency_total_ms counter",
            f"exsoftoptic_request_latency_total_ms {snapshot['latency_total_ms']}",
            "# HELP exsoftoptic_requests_in_flight Current HTTP requests being processed",
            "# TYPE exsoftoptic_requests_in_flight gauge",
            f"exsoftoptic_requests_in_flight {snapshot['in_flight']}",
            "# HELP exsoftoptic_request_latency_ms Request latency histogram in milliseconds",
            "# TYPE exsoftoptic_request_latency_ms histogram",
            "# HELP exsoftoptic_responses_total Total HTTP responses grouped by status code",
            "# TYPE exsoftoptic_responses_total counter",
        ]
        for boundary, count in snapshot["latency_buckets_ms"].items():
            lines.append(f'exsoftoptic_request_latency_ms_bucket{{le="{boundary}"}} {count}')
        lines.append(f'exsoftoptic_request_latency_ms_bucket{{le="+Inf"}} {snapshot["requests_total"]}')
        lines.append(f'exsoftoptic_request_latency_ms_sum {snapshot["latency_total_ms"]}')
        lines.append(f'exsoftoptic_request_latency_ms_count {snapshot["requests_total"]}')
        for status_code, count in snapshot["responses_by_status"].items():
            lines.append(f'exsoftoptic_responses_total{{status_code="{status_code}"}} {count}')
        lines.extend([
            "# HELP exsoftoptic_route_responses_total Total HTTP responses grouped by method, path and status code",
            "# TYPE exsoftoptic_route_responses_total counter",
        ])
        for route in snapshot["responses_by_route"]:
            lines.append(
                "exsoftoptic_route_responses_total"
                f'{{method="{route["method"]}",path="{route["path"]}",status_code="{route["status_code"]}"}} {route["count"]}'
            )
        return "\n".join(lines) + "\n"


runtime_metrics = RuntimeMetrics()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Registra métricas básicas de latencia/estado y expone tiempo de proceso."""

    def __init__(self, app, *, metrics: RuntimeMetrics | None = None) -> None:
        super().__init__(app)
        self.metrics = metrics or runtime_metrics

    async def dispatch(self, request: Request, call_next) -> Response:
        started_at = time.perf_counter()
        self.metrics.request_started()
        try:
            response = await call_next(request)
        except Exception:
            latency_ms = (time.perf_counter() - started_at) * 1000
            self.metrics.record_exception(latency_ms=latency_ms)
            raise
        finally:
            self.metrics.request_finished()

        latency_ms = (time.perf_counter() - started_at) * 1000
        route = request.scope.get("route") if hasattr(request, "scope") else None
        path = getattr(route, "path", request.url.path)
        self.metrics.record_response(status_code=response.status_code, latency_ms=latency_ms, method=request.method, path=path)
        response.headers["X-Process-Time-ms"] = f"{latency_ms:.3f}"
        return response
