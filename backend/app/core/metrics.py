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
            }


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
