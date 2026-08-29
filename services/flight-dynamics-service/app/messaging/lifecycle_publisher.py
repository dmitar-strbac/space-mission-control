from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    SimulationLifecycleSubject,
)

from app.core.config import get_settings
from app.domain.runtime import SimulationRuntime
from app.models.simulation_session import SimulationSession

settings = get_settings()


async def publish_simulation_completed(
    *,
    event_bus: EventBus,
    simulation: SimulationSession,
    runtime: SimulationRuntime,
) -> None:
    envelope = EventEnvelope.create(
        event_type=(SimulationLifecycleSubject.COMPLETED.value),
        source=settings.service_name,
        correlation_id=str(simulation.mission_id),
        payload={
            "mission_id": str(simulation.mission_id),
            "simulation_session_id": str(simulation.id),
            "simulation_time_s": (runtime.state.elapsed_time_s),
        },
    )

    await event_bus.publish(
        subject=(SimulationLifecycleSubject.COMPLETED.value),
        envelope=envelope,
    )


async def publish_simulation_failed(
    *,
    event_bus: EventBus,
    mission_id: UUID,
    reason: str,
    simulation_session_id: UUID | None = None,
) -> None:
    payload: dict[str, object] = {
        "mission_id": str(mission_id),
        "reason": reason,
    }

    if simulation_session_id is not None:
        payload["simulation_session_id"] = str(simulation_session_id)

    envelope = EventEnvelope.create(
        event_type=(SimulationLifecycleSubject.FAILED.value),
        source=settings.service_name,
        correlation_id=str(mission_id),
        payload=payload,
    )

    await event_bus.publish(
        subject=(SimulationLifecycleSubject.FAILED.value),
        envelope=envelope,
    )
