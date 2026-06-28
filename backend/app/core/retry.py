import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    base_delay_seconds: float = 0.1
    max_delay_seconds: float = 2.0
    retry_exceptions: tuple[type[BaseException], ...] = (Exception,)


async def retry_async(operation: Callable[[], Awaitable[T]], policy: RetryPolicy) -> T:
    """Retry an async operation with exponential backoff."""
    if policy.attempts < 1:
        raise ValueError("Retry attempts must be greater than zero")
    last_error: BaseException | None = None
    for attempt in range(policy.attempts):
        try:
            return await operation()
        except policy.retry_exceptions as exc:
            last_error = exc
            if attempt == policy.attempts - 1:
                break
            delay = min(policy.max_delay_seconds, policy.base_delay_seconds * (2**attempt))
            await asyncio.sleep(delay)
    assert last_error is not None
    raise last_error
