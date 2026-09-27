import time
from dataclasses import dataclass
from threading import Lock
from typing import Iterable

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import get_request_context


@dataclass
class _Bucket:
    window_started_at: float
    count: int
    last_seen_at: float


class InMemoryRateLimiter:
    """Rate limiter fijo por ventana para proteger endpoints ante abuso básico."""

    def __init__(self, *, limit: int = 120, window_seconds: int = 60, max_clients: int = 10_000) -> None:
        if limit <= 0:
            raise ValueError("limit debe ser mayor que cero")
        if window_seconds <= 0:
            raise ValueError("window_seconds debe ser mayor que cero")
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self._buckets: dict[str, _Bucket] = {}
        self._lock = Lock()

    def check(self, key: str, now: float | None = None) -> tuple[bool, int, int]:
        """Registra una solicitud y retorna permitido, restante y epoch de reinicio."""
        current_time = now if now is not None else time.monotonic()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None or current_time - bucket.window_started_at >= self.window_seconds:
                bucket = _Bucket(window_started_at=current_time, count=0, last_seen_at=current_time)
                self._buckets[key] = bucket

            bucket.count += 1
            bucket.last_seen_at = current_time
            allowed = bucket.count <= self.limit
            remaining = max(self.limit - bucket.count, 0)
            reset_after = max(int(bucket.window_started_at + self.window_seconds - current_time), 0)

            if len(self._buckets) > self.max_clients:
                self._prune(current_time)

            return allowed, remaining, reset_after

    def _prune(self, current_time: float) -> None:
        expired_before = current_time - (self.window_seconds * 2)
        expired_keys = [key for key, bucket in self._buckets.items() if bucket.last_seen_at < expired_before]
        for key in expired_keys:
            self._buckets.pop(key, None)

        if len(self._buckets) > self.max_clients:
            oldest_keys = sorted(self._buckets, key=lambda item: self._buckets[item].last_seen_at)
            for key in oldest_keys[: len(self._buckets) - self.max_clients]:
                self._buckets.pop(key, None)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Aplica límites por IP sin depender de infraestructura externa."""

    def __init__(
        self,
        app,
        *,
        limit: int = 120,
        window_seconds: int = 60,
        excluded_paths: Iterable[str] | None = None,
        limiter: InMemoryRateLimiter | None = None,
    ) -> None:
        super().__init__(app)
        self.limiter = limiter or InMemoryRateLimiter(limit=limit, window_seconds=window_seconds)
        self.excluded_paths = set(excluded_paths or {"/", "/health", "/ready", "/docs", "/redoc", "/openapi.json"})

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        client_key = self._client_key(request)
        allowed, remaining, reset_after = self.limiter.check(client_key)
        headers = self._headers(remaining=remaining, reset_after=reset_after)

        if not allowed:
            context = get_request_context()
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Demasiadas solicitudes. Intente nuevamente más tarde.",
                        "details": {
                            "limit": self.limiter.limit,
                            "window_seconds": self.limiter.window_seconds,
                            "reset_after_seconds": reset_after,
                        },
                        "correlation_id": context.correlation_id if context else None,
                    }
                },
                headers=headers,
            )

        response = await call_next(request)
        for name, value in headers.items():
            response.headers[name] = value
        return response

    def _headers(self, *, remaining: int, reset_after: int) -> dict[str, str]:
        return {
            "X-RateLimit-Limit": str(self.limiter.limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_after),
        }

    def _client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "anonymous"
