import time
from collections import defaultdict
from threading import Lock
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RuntimeMetrics:
    """Contadores runtime en memoria para observabilidad operativa ligera."""

    def __init__(self) -> None:
        self.started_at = time.time()
        self._started_monotonic = time.monotonic()
        self._requests_total = 0
        self._responses_by_status: dict[int, int] = defaultdict(int)
        self._exceptions_total = 0
        self._latency_total_ms = 0.0
        self._lock = Lock()

    def record_response(self, *, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self._requests_total += 1
            self._responses_by_status[status_code] += 1
            self._latency_total_ms += latency_ms

    def record_exception(self, *, latency_ms: float) -> None:
        with self._lock:
            self._requests_total += 1
            self._exceptions_total += 1
            self._latency_total_ms += latency_ms

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
            "# HELP exsoftoptic_responses_total Total HTTP responses grouped by status code",
            "# TYPE exsoftoptic_responses_total counter",
        ]
        for status_code, count in snapshot["responses_by_status"].items():
            lines.append(f'exsoftoptic_responses_total{{status_code="{status_code}"}} {count}')
        return "\n".join(lines) + "\n"


runtime_metrics = RuntimeMetrics()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Registra métricas básicas de latencia/estado y expone tiempo de proceso."""

    def __init__(self, app, *, metrics: RuntimeMetrics | None = None) -> None:
        super().__init__(app)
        self.metrics = metrics or runtime_metrics

    async def dispatch(self, request: Request, call_next) -> Response:
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            latency_ms = (time.perf_counter() - started_at) * 1000
            self.metrics.record_exception(latency_ms=latency_ms)
            raise

        latency_ms = (time.perf_counter() - started_at) * 1000
        self.metrics.record_response(status_code=response.status_code, latency_ms=latency_ms)
        response.headers["X-Process-Time-ms"] = f"{latency_ms:.3f}"
        return response
