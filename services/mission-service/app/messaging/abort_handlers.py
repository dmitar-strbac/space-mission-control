from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from smc_messaging import (
    AbortSubject,
    EventBus,
    EventEnvelope,
    SafetySubject,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionFactory
from app.services.abort_workflow import AbortWorkflowService
from app.services.idempotency_service import IdempotencyService
from app.services.mission_service import MissionService

AbortHandler = Callable[
    [AsyncSession, EventEnvelope],
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


async def register_abort_handlers(
    event_bus: EventBus,
) -> None:
    async def _run_once(
        envelope: EventEnvelope,
        handler: AbortHandler,
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

    async def safety_abort_recommended(
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
                "Safety system recommended mission abort.",
            )
        )

        await AbortWorkflowService(
            MissionService(session),
            event_bus,
        ).request_abort(
            mission_id,
            reason=reason,
            causation_id=envelope.event_id,
        )

    async def simulation_abort_completed(
        session: AsyncSession,
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        await AbortWorkflowService(
            MissionService(session),
            event_bus,
        ).complete_abort(mission_id)

    async def abort_failed(
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
                "Emergency Abort workflow failed.",
            )
        )

        await AbortWorkflowService(
            MissionService(session),
            event_bus,
        ).fail_abort(
            mission_id,
            reason=reason,
        )

    async def safety_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(
            envelope,
            safety_abort_recommended,
        )

    async def completed_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(
            envelope,
            simulation_abort_completed,
        )

    async def failed_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(
            envelope,
            abort_failed,
        )

    await event_bus.subscribe(
        subject=SafetySubject.ABORT_RECOMMENDED.value,
        durable_name="mission-abort-safety-worker",
        handler=safety_handler,
    )

    await event_bus.subscribe(
        subject=(AbortSubject.SIMULATION_ABORT_COMPLETED.value),
        durable_name="mission-abort-completed-worker",
        handler=completed_handler,
    )

    await event_bus.subscribe(
        subject=AbortSubject.ABORT_FAILED.value,
        durable_name="mission-abort-failed-worker",
        handler=failed_handler,
    )
