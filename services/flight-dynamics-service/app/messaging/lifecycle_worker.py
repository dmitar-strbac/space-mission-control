from typing import Any
from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    SimulationLifecycleSubject,
)

from app.core.database import SessionFactory
from app.messaging.lifecycle_publisher import publish_simulation_failed
from app.services.idempotency_service import IdempotencyService
from app.services.simulation_runtime import simulation_runtime_manager
from app.services.simulation_service import SimulationService


def _require_uuid(
    payload: dict[str, Any],
    field: str,
) -> UUID:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return UUID(str(value))


async def register_simulation_lifecycle_worker(
    event_bus: EventBus,
) -> None:
    async def start_simulation(
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        try:
            async with SessionFactory() as session:
                await SimulationService(session).start(mission_id)

            simulation_runtime_manager.start(mission_id)

        except Exception as error:
            await publish_simulation_failed(
                event_bus=event_bus,
                mission_id=mission_id,
                reason=str(error),
            )

    async def start_handler(
        envelope: EventEnvelope,
    ) -> None:
        async with SessionFactory() as session:
            idempotency = IdempotencyService(session)

            if await idempotency.was_processed(envelope):
                return

        await start_simulation(envelope)

        async with SessionFactory() as session:
            await IdempotencyService(session).mark_processed(envelope)

    await event_bus.subscribe(
        subject=(SimulationLifecycleSubject.START_REQUESTED.value),
        durable_name=("flight-dynamics-simulation-start-worker"),
        handler=start_handler,
    )
