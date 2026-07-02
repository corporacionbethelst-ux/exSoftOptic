from contextvars import ContextVar
from dataclasses import dataclass
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


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Propaga metadatos técnicos de request para auditoría y trazabilidad."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        forwarded_for = request.headers.get("X-Forwarded-For")
        ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else None)
        token = _request_context.set(
            RequestContext(
                correlation_id=correlation_id,
                ip_address=ip_address,
                user_agent=request.headers.get("User-Agent"),
            )
        )
        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            _request_context.reset(token)


def get_request_context() -> RequestContext | None:
    return _request_context.get()
