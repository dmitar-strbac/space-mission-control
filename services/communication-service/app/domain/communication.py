from dataclasses import dataclass

from app.domain.enums import SignalStatus
from app.domain.exceptions import InvalidCommunicationProfileError

SPEED_OF_LIGHT_M_S = 299_792_458.0


@dataclass(frozen=True)
class CommunicationDelay:
    propagation_delay_s: float
    additional_latency_s: float

    @property
    def total_delay_s(self) -> float:
        return self.propagation_delay_s + self.additional_latency_s


def calculate_propagation_delay_s(
    distance_m: float,
) -> float:
    if distance_m < 0:
        raise InvalidCommunicationProfileError(
            "Communication distance cannot be negative.",
            details={"distance_m": distance_m},
        )

    return distance_m / SPEED_OF_LIGHT_M_S


def calculate_communication_delay(
    *,
    distance_m: float,
    additional_latency_ms: float,
) -> CommunicationDelay:
    if additional_latency_ms < 0:
        raise InvalidCommunicationProfileError(
            "Additional network latency cannot be negative.",
            details={
                "additional_latency_ms": additional_latency_ms,
            },
        )

    return CommunicationDelay(
        propagation_delay_s=calculate_propagation_delay_s(distance_m),
        additional_latency_s=additional_latency_ms / 1000.0,
    )


def validate_packet_loss_percent(
    packet_loss_percent: float,
) -> None:
    if not 0.0 <= packet_loss_percent <= 100.0:
        raise InvalidCommunicationProfileError(
            "Packet loss percentage must be between 0 and 100.",
            details={
                "packet_loss_percent": packet_loss_percent,
            },
        )


def should_lose_packet(
    *,
    packet_loss_percent: float,
    sample: float,
) -> bool:
    validate_packet_loss_percent(packet_loss_percent)

    if not 0.0 <= sample < 1.0:
        raise ValueError("sample must be greater than or equal to 0 and less than 1")

    return sample < packet_loss_percent / 100.0


def can_transmit(signal_status: SignalStatus) -> bool:
    return signal_status != SignalStatus.LOST
