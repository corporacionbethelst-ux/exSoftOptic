from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import TypeVar


T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    pass


@dataclass(frozen=True)
class CircuitSnapshot:
    state: CircuitState
    consecutive_failures: int
    opened_at: float | None


class CircuitBreaker:
    """Small process-local circuit breaker for external provider adapters."""

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
        should_count_failure: Callable[[BaseException], bool] | None = None,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be greater than zero")
        if recovery_timeout_seconds < 0:
            raise ValueError("recovery_timeout_seconds cannot be negative")
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self._clock = clock
        self._should_count_failure = should_count_failure
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._opened_at: float | None = None
        self._half_open_request_in_flight = False
        self._lock = Lock()

    def snapshot(self) -> CircuitSnapshot:
        with self._lock:
            return CircuitSnapshot(
                state=self._state,
                consecutive_failures=self._consecutive_failures,
                opened_at=self._opened_at,
            )

    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        self._before_call()
        try:
            result = await operation()
        except Exception as exc:
            if self._should_count_failure is None or self._should_count_failure(exc):
                self._record_failure()
            else:
                self._record_success()
            raise
        self._record_success()
        return result

    def _before_call(self) -> None:
        with self._lock:
            if self._state == CircuitState.OPEN:
                elapsed = self._clock() - (self._opened_at or 0.0)
                if elapsed < self.recovery_timeout_seconds:
                    raise CircuitOpenError("External provider circuit is open")
                self._state = CircuitState.HALF_OPEN
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_request_in_flight:
                    raise CircuitOpenError("External provider circuit is half-open")
                self._half_open_request_in_flight = True

    def _record_success(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._consecutive_failures = 0
            self._opened_at = None
            self._half_open_request_in_flight = False

    def _record_failure(self) -> None:
        with self._lock:
            self._half_open_request_in_flight = False
            self._consecutive_failures += 1
            if (
                self._state == CircuitState.HALF_OPEN
                or self._consecutive_failures >= self.failure_threshold
            ):
                self._state = CircuitState.OPEN
                self._opened_at = self._clock()
