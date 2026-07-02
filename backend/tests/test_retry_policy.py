import pytest

from app.core.retry import RetryPolicy, retry_async


@pytest.mark.asyncio
async def test_retry_async_retries_until_success():
    calls = 0

    async def operation():
        nonlocal calls
        calls += 1
        if calls < 2:
            raise RuntimeError("transient")
        return "ok"

    result = await retry_async(operation, RetryPolicy(attempts=3, base_delay_seconds=0, retry_exceptions=(RuntimeError,)))

    assert result == "ok"
    assert calls == 2


@pytest.mark.asyncio
async def test_retry_async_raises_last_error_after_attempts():
    async def operation():
        raise RuntimeError("still failing")

    with pytest.raises(RuntimeError, match="still failing"):
        await retry_async(operation, RetryPolicy(attempts=2, base_delay_seconds=0, retry_exceptions=(RuntimeError,)))


@pytest.mark.asyncio
async def test_retry_async_rejects_invalid_attempts():
    async def operation():
        return "unused"

    with pytest.raises(ValueError):
        await retry_async(operation, RetryPolicy(attempts=0))
