from types import SimpleNamespace

import pytest
from starlette.datastructures import URL
from starlette.responses import Response

from app.core.error_handlers import _error_payload
from app.core.security_headers import SecurityHeadersMiddleware


def test_error_payload_has_standard_shape_without_context():
    payload = _error_payload(code="X", message="Mensaje", details={"field": "value"})

    assert payload["error"]["code"] == "X"
    assert payload["error"]["message"] == "Mensaje"
    assert payload["error"]["details"] == {"field": "value"}
    assert "correlation_id" in payload["error"]


@pytest.mark.asyncio
async def test_security_headers_middleware_adds_defensive_headers():
    middleware = SecurityHeadersMiddleware(app=lambda scope, receive, send: None)
    request = SimpleNamespace(url=URL("https://example.test/health"))

    async def call_next(_request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
