import json
from types import SimpleNamespace

import pytest
from starlette.datastructures import URL
from starlette.responses import Response

from app.core.metrics import MetricsMiddleware, RuntimeMetrics
from app.core.rate_limit import InMemoryRateLimiter, RateLimitMiddleware


@pytest.mark.asyncio
async def test_rate_limit_middleware_blocks_after_limit():
    limiter = InMemoryRateLimiter(limit=1, window_seconds=60)
    middleware = RateLimitMiddleware(app=None, limiter=limiter)
    request = SimpleNamespace(
        url=URL("http://testserver/api/v1/inventario"),
        headers={},
        client=SimpleNamespace(host="127.0.0.1"),
    )

    async def call_next(_request):
        return Response("ok", status_code=200)

    first_response = await middleware.dispatch(request, call_next)
    second_response = await middleware.dispatch(request, call_next)

    assert first_response.status_code == 200
    assert first_response.headers["X-RateLimit-Limit"] == "1"
    assert second_response.status_code == 429
    assert json.loads(second_response.body)["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_metrics_middleware_records_latency_and_status():
    metrics = RuntimeMetrics()
    middleware = MetricsMiddleware(app=None, metrics=metrics)
    request = SimpleNamespace(url=URL("http://testserver/api/v1/ventas"), headers={}, client=None)

    async def call_next(_request):
        return Response("ok", status_code=201)

    response = await middleware.dispatch(request, call_next)
    snapshot = metrics.snapshot()

    assert response.status_code == 201
    assert "X-Process-Time-ms" in response.headers
    assert snapshot["requests_total"] == 1
    assert snapshot["responses_by_status"] == {"201": 1}
    assert snapshot["exceptions_total"] == 0


@pytest.mark.asyncio
async def test_metrics_middleware_records_exceptions():
    metrics = RuntimeMetrics()
    middleware = MetricsMiddleware(app=None, metrics=metrics)
    request = SimpleNamespace(url=URL("http://testserver/api/v1/ventas"), headers={}, client=None)

    async def call_next(_request):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await middleware.dispatch(request, call_next)

    snapshot = metrics.snapshot()
    assert snapshot["requests_total"] == 1
    assert snapshot["exceptions_total"] == 1
