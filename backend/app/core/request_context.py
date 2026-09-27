from contextvars import ContextVar
from dataclasses import dataclass
import logging
import re
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


@dataclass(frozen=True)
class RequestContext:
    correlation_id: str
    ip_address: str | None
    user_agent: str | None


_request_context: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)
logger = logging.getLogger("exsoftoptic.http")
_CORRELATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def safe_correlation_id(candidate: str | None) -> str:
    if candidate and _CORRELATION_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Propaga metadatos técnicos de request para auditoría y trazabilidad."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = safe_correlation_id(request.headers.get("X-Correlation-ID"))
        forwarded_for = request.headers.get("X-Forwarded-For")
        ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else None)
        token = _request_context.set(
            RequestContext(
                correlation_id=correlation_id,
                ip_address=ip_address,
                user_agent=request.headers.get("User-Agent"),
            )
        )
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            route = request.scope.get("route")
            route_path = getattr(route, "path", request.url.path)
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": route_path,
                    "status_code": response.status_code,
                    "duration_ms": round((time.perf_counter() - started_at) * 1000, 3),
                    "client_ip": ip_address,
                },
            )
            return response
        except Exception:
            logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round((time.perf_counter() - started_at) * 1000, 3),
                    "client_ip": ip_address,
                },
            )
            raise
        finally:
            _request_context.reset(token)


def get_request_context() -> RequestContext | None:
    return _request_context.get()
