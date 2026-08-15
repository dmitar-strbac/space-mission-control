from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    IntegrationSubject,
)

from app.core.config import get_settings
from app.domain.communication import calculate_communication_delay
from app.models.communication_profile import CommunicationProfile

settings = get_settings()


async def publish_communication_status(
    *,
    event_bus: EventBus,
    profile: CommunicationProfile,
    causation_id: UUID | str | None = None,
) -> None:
    delay = calculate_communication_delay(
        distance_m=profile.distance_m,
        additional_latency_ms=profile.additional_latency_ms,
    )

    envelope = EventEnvelope.create(
        event_type=(IntegrationSubject.COMMUNICATION_STATUS_UPDATED.value),
        source=settings.service_name,
        correlation_id=str(profile.mission_id),
        causation_id=causation_id,
        payload={
            "mission_id": str(profile.mission_id),
            "signal_status": profile.signal_status.value,
            "one_way_delay_ms": (delay.total_delay_s * 1000.0),
            "packet_loss_percent": (profile.packet_loss_percent),
            "observed_at": profile.updated_at.isoformat(),
        },
    )

    await event_bus.publish(
        subject=(IntegrationSubject.COMMUNICATION_STATUS_UPDATED.value),
        envelope=envelope,
    )
