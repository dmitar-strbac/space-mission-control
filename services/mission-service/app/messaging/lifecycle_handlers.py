from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any
from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    SimulationLifecycleSubject,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionFactory
from app.services.idempotency_service import IdempotencyService
from app.services.mission_service import MissionService

LifecycleHandler = Callable[
    [
        AsyncSession,
        EventEnvelope,
    ],
    Awaitable[None],
]


def _require_uuid(
    payload: dict[str, Any],
    field: str,
) -> UUID:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return UUID(str(value))


async def register_simulation_lifecycle_handlers(
    event_bus: EventBus,
) -> None:
    async def _run_once(
        envelope: EventEnvelope,
        handler: LifecycleHandler,
    ) -> None:
        async with SessionFactory() as session:
            idempotency = IdempotencyService(session)

            if await idempotency.was_processed(envelope):
                return

            await handler(
                session,
                envelope,
            )

            await idempotency.mark_processed(envelope)

    async def simulation_completed(
        session: AsyncSession,
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        await MissionService(session).complete(mission_id)

    async def simulation_failed(
        session: AsyncSession,
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        reason = str(
            envelope.payload.get(
                "reason",
                ("Flight Dynamics simulation failed."),
            )
        )

        await MissionService(session).fail(
            mission_id,
            reason=reason,
        )

    async def completed_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(
            envelope,
            simulation_completed,
        )

    async def failed_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(
            envelope,
            simulation_failed,
        )

    await event_bus.subscribe(
        subject=(SimulationLifecycleSubject.COMPLETED.value),
        durable_name=("mission-simulation-completed-worker"),
        handler=completed_handler,
    )

    await event_bus.subscribe(
        subject=(SimulationLifecycleSubject.FAILED.value),
        durable_name=("mission-simulation-failed-worker"),
        handler=failed_handler,
    )
