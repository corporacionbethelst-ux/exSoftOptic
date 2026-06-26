import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_context import get_request_context

logger = logging.getLogger(__name__)


def _error_payload(*, code: str, message: str, details: Any = None) -> dict[str, Any]:
    context = get_request_context()
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "correlation_id": context.correlation_id if context else None,
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload(code="VALIDATION_ERROR", message="Datos de entrada inválidos", details=exc.errors()),
        )

    @app.exception_handler(HTTPException)
    async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(code="HTTP_ERROR", message=str(exc.detail), details=None),
            headers=exc.headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(code="HTTP_ERROR", message=str(exc.detail), details=None),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled backend error", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(code="INTERNAL_SERVER_ERROR", message="Error interno del servidor", details=None),
        )
