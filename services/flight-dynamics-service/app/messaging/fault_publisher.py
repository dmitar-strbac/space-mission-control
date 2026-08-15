from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    FaultSubject,
)

from app.core.config import get_settings
from app.domain.faults import ActiveFault, FaultType

settings = get_settings()


async def publish_fault_injected(
    *,
    event_bus: EventBus,
    mission_id: UUID,
    fault: ActiveFault,
) -> None:
    envelope = EventEnvelope.create(
        event_type=FaultSubject.FAULT_INJECTED.value,
        source=settings.service_name,
        correlation_id=str(mission_id),
        payload={
            "mission_id": str(mission_id),
            "fault_type": fault.fault_type.value,
            "magnitude": fault.magnitude,
            "affected_service": settings.service_name,
        },
    )

    await event_bus.publish(
        subject=FaultSubject.FAULT_INJECTED.value,
        envelope=envelope,
    )


async def publish_fault_cleared(
    *,
    event_bus: EventBus,
    mission_id: UUID,
    fault_type: FaultType,
) -> None:
    envelope = EventEnvelope.create(
        event_type=FaultSubject.FAULT_CLEARED.value,
        source=settings.service_name,
        correlation_id=str(mission_id),
        payload={
            "mission_id": str(mission_id),
            "fault_type": fault_type.value,
            "affected_service": settings.service_name,
        },
    )

    await event_bus.publish(
        subject=FaultSubject.FAULT_CLEARED.value,
        envelope=envelope,
    )
