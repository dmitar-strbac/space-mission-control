import pytest

from app.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)


async def test_circuit_breaker_opens_after_failure_threshold() -> None:
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout_seconds=30.0,
    )

    await breaker.record_failure()

    assert breaker.state is CircuitState.CLOSED

    await breaker.record_failure()

    assert breaker.state is CircuitState.OPEN

    with pytest.raises(CircuitBreakerOpenError):
        await breaker.before_request()


async def test_success_resets_circuit_breaker() -> None:
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=30.0,
    )

    await breaker.record_failure()

    assert breaker.state is CircuitState.OPEN

    await breaker.record_success()

    assert breaker.state is CircuitState.CLOSED
    assert breaker.failure_count == 0
