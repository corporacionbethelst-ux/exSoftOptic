import asyncio
import random
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
    jitter_ratio: float = 0.2
    should_retry: Callable[[BaseException], bool] | None = None


async def retry_async(operation: Callable[[], Awaitable[T]], policy: RetryPolicy) -> T:
    """Retry an async operation with exponential backoff."""
    if policy.attempts < 1:
        raise ValueError("Retry attempts must be greater than zero")
    if policy.base_delay_seconds < 0 or policy.max_delay_seconds < 0:
        raise ValueError("Retry delays cannot be negative")
    if not 0 <= policy.jitter_ratio <= 1:
        raise ValueError("Retry jitter_ratio must be between zero and one")
    last_error: BaseException | None = None
    for attempt in range(policy.attempts):
        try:
            return await operation()
        except policy.retry_exceptions as exc:
            last_error = exc
            if attempt == policy.attempts - 1 or (
                policy.should_retry is not None and not policy.should_retry(exc)
            ):
                break
            base_delay = min(
                policy.max_delay_seconds, policy.base_delay_seconds * (2**attempt)
            )
            jitter = base_delay * policy.jitter_ratio * random.random()
            delay = min(policy.max_delay_seconds, base_delay + jitter)
            await asyncio.sleep(delay)
    assert last_error is not None
    raise last_error
