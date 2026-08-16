import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from time import monotonic


class CircuitState(StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    pass


@dataclass
class CircuitBreaker:
    failure_threshold: int
    recovery_timeout_seconds: float
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _opened_at: float | None = field(default=None, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    @property
    def state(self) -> CircuitState:
        return self._state

    @property
    def failure_count(self) -> int:
        return self._failure_count

    async def before_request(self) -> None:
        async with self._lock:
            if self._state is CircuitState.CLOSED:
                return

            if self._state is CircuitState.HALF_OPEN:
                raise CircuitBreakerOpenError

            if self._opened_at is None:
                raise CircuitBreakerOpenError

            elapsed = monotonic() - self._opened_at

            if elapsed < self.recovery_timeout_seconds:
                raise CircuitBreakerOpenError

            self._state = CircuitState.HALF_OPEN

    async def record_success(self) -> None:
        async with self._lock:
            self._failure_count = 0
            self._opened_at = None
            self._state = CircuitState.CLOSED

    async def record_failure(self) -> None:
        async with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._open()
                return

            self._failure_count += 1

            if self._failure_count >= self.failure_threshold:
                self._open()

    def _open(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = monotonic()
