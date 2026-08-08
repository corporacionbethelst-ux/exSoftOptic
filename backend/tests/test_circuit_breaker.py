import asyncio

import pytest

from app.core.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState


@pytest.mark.asyncio
async def test_circuit_opens_and_rejects_calls_after_threshold():
    calls = 0
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=60)

    async def failing():
        nonlocal calls
        calls += 1
        raise RuntimeError("provider down")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            await breaker.call(failing)

    assert breaker.snapshot().state == CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        await breaker.call(failing)
    assert calls == 2


@pytest.mark.asyncio
async def test_circuit_half_open_probe_recovers_after_timeout():
    now = [100.0]
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=10,
        clock=lambda: now[0],
    )

    async def failing():
        raise RuntimeError("provider down")

    with pytest.raises(RuntimeError):
        await breaker.call(failing)
    now[0] += 10

    assert await breaker.call(lambda: asyncio.sleep(0, result="ok")) == "ok"
    assert breaker.snapshot().state == CircuitState.CLOSED
    assert breaker.snapshot().consecutive_failures == 0


@pytest.mark.asyncio
async def test_non_counted_failure_does_not_open_circuit():
    breaker = CircuitBreaker(
        failure_threshold=1,
        should_count_failure=lambda exc: not isinstance(exc, ValueError),
    )

    async def invalid_request():
        raise ValueError("client error")

    with pytest.raises(ValueError):
        await breaker.call(invalid_request)
    assert breaker.snapshot().state == CircuitState.CLOSED
