import asyncio
from typing import Any
from uuid import UUID

from smc_messaging import (
    AbortSubject,
    EventBus,
    EventEnvelope,
)

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.domain.enums import CommandType
from app.schemas.command import CommandCreateRequest
from app.services.command_service import CommandService
from app.services.idempotency_service import IdempotencyService

settings = get_settings()


def _require_uuid(
    payload: dict[str, Any],
    field: str,
) -> UUID:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return UUID(str(value))


async def _publish_abort_event(
    *,
    event_bus: EventBus,
    source_event: EventEnvelope,
    subject: AbortSubject,
    payload: dict[str, object],
) -> None:
    envelope = EventEnvelope.create(
        event_type=subject.value,
        source=settings.service_name,
        correlation_id=source_event.correlation_id,
        causation_id=source_event.event_id,
        payload=payload,
    )

    await event_bus.publish(
        subject=subject.value,
        envelope=envelope,
    )


async def register_abort_worker(
    event_bus: EventBus,
) -> None:
    async def process_abort(
        envelope: EventEnvelope,
    ) -> None:
        async with SessionFactory() as session:
            idempotency = IdempotencyService(session)

            if await idempotency.was_processed(envelope):
                return

        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        reason = str(
            envelope.payload.get(
                "reason",
                "Emergency Abort requested.",
            )
        )

        try:
            async with SessionFactory() as session:
                service = CommandService(session)

                command = await service.create(
                    CommandCreateRequest(
                        mission_id=mission_id,
                        command_type=(CommandType.EMERGENCY_ABORT),
                        payload={
                            "reason": reason,
                        },
                    )
                )

                command = await service.queue(command.id)

                await _publish_abort_event(
                    event_bus=event_bus,
                    source_event=envelope,
                    subject=(AbortSubject.COMMAND_ABORT_QUEUED),
                    payload={
                        "mission_id": str(mission_id),
                        "command_id": str(command.id),
                    },
                )

                (
                    command,
                    delay_ms,
                ) = await service.dispatch(command.id)

                await asyncio.sleep(delay_ms / 1000.0)

                command = await service.deliver(command.id)

                await _publish_abort_event(
                    event_bus=event_bus,
                    source_event=envelope,
                    subject=(AbortSubject.COMMAND_ABORT_DELIVERED),
                    payload={
                        "mission_id": str(mission_id),
                        "command_id": str(command.id),
                        "one_way_delay_ms": delay_ms,
                    },
                )

                command = await service.execute(command.id)

                await _publish_abort_event(
                    event_bus=event_bus,
                    source_event=envelope,
                    subject=(AbortSubject.COMMAND_ABORT_EXECUTED),
                    payload={
                        "mission_id": str(mission_id),
                        "command_id": str(command.id),
                    },
                )

            async with SessionFactory() as session:
                await IdempotencyService(session).mark_processed(envelope)

        except Exception as error:
            await _publish_abort_event(
                event_bus=event_bus,
                source_event=envelope,
                subject=AbortSubject.ABORT_FAILED,
                payload={
                    "mission_id": str(mission_id),
                    "failed_service": (settings.service_name),
                    "reason": str(error),
                },
            )

    await event_bus.subscribe(
        subject=(AbortSubject.MISSION_ABORT_REQUESTED.value),
        durable_name=("communication-emergency-abort-worker"),
        handler=process_abort,
    )
