import pytest

from app.domain.communication import (
    SPEED_OF_LIGHT_M_S,
    calculate_communication_delay,
    calculate_propagation_delay_s,
    can_transmit,
    should_lose_packet,
)
from app.domain.enums import SignalStatus
from app.domain.exceptions import (
    InvalidCommunicationProfileError,
)


def test_zero_distance_has_zero_propagation_delay() -> None:
    delay = calculate_propagation_delay_s(0.0)

    assert delay == pytest.approx(0.0)


def test_propagation_delay_uses_speed_of_light() -> None:
    delay = calculate_propagation_delay_s(SPEED_OF_LIGHT_M_S)

    assert delay == pytest.approx(1.0)


def test_lunar_distance_has_realistic_one_way_delay() -> None:
    delay = calculate_propagation_delay_s(384_400_000.0)

    assert delay == pytest.approx(
        1.2822,
        rel=1e-3,
    )


def test_total_delay_includes_network_latency() -> None:
    delay = calculate_communication_delay(
        distance_m=400_000.0,
        additional_latency_ms=40.0,
    )

    assert delay.propagation_delay_s == pytest.approx(
        0.001334,
        rel=1e-3,
    )

    assert delay.additional_latency_s == pytest.approx(0.04)

    assert delay.total_delay_s == pytest.approx(
        0.041334,
        rel=1e-3,
    )


def test_negative_distance_is_rejected() -> None:
    with pytest.raises(InvalidCommunicationProfileError):
        calculate_propagation_delay_s(-1.0)


def test_negative_network_latency_is_rejected() -> None:
    with pytest.raises(InvalidCommunicationProfileError):
        calculate_communication_delay(
            distance_m=100.0,
            additional_latency_ms=-1.0,
        )


def test_packet_is_lost_when_sample_is_below_probability() -> None:
    assert should_lose_packet(
        packet_loss_percent=10.0,
        sample=0.05,
    )


def test_packet_is_not_lost_when_sample_is_above_probability() -> None:
    assert not should_lose_packet(
        packet_loss_percent=10.0,
        sample=0.50,
    )


@pytest.mark.parametrize(
    "packet_loss_percent",
    [-1.0, 101.0],
)
def test_invalid_packet_loss_is_rejected(
    packet_loss_percent: float,
) -> None:
    with pytest.raises(InvalidCommunicationProfileError):
        should_lose_packet(
            packet_loss_percent=packet_loss_percent,
            sample=0.5,
        )


@pytest.mark.parametrize(
    "sample",
    [-0.1, 1.0],
)
def test_invalid_packet_sample_is_rejected(
    sample: float,
) -> None:
    with pytest.raises(ValueError):
        should_lose_packet(
            packet_loss_percent=10.0,
            sample=sample,
        )


def test_available_signal_can_transmit() -> None:
    assert can_transmit(SignalStatus.AVAILABLE)


def test_degraded_signal_can_transmit() -> None:
    assert can_transmit(SignalStatus.DEGRADED)


def test_lost_signal_cannot_transmit() -> None:
    assert not can_transmit(SignalStatus.LOST)
