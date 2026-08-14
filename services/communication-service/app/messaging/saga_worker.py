from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    SagaSubject,
)

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.domain.enums import SignalStatus
from app.messaging.status_publisher import publish_communication_status
from app.schemas.communication_profile import CommunicationProfileCreateRequest
from app.services.communication_service import CommunicationService
from app.services.idempotency_service import IdempotencyService

settings = get_settings()


def _require_dict(
    payload: dict[str, Any],
    field: str,
) -> dict[str, Any]:
    value = payload.get(field)

    if not isinstance(value, dict):
        raise ValueError(f"Event payload field '{field}' must be an object.")

    return value


def _require_uuid(
    payload: dict[str, Any],
    field: str,
) -> UUID:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return UUID(str(value))


def _communication_distance(
    mission: dict[str, Any],
) -> float:
    target_parameters = _require_dict(
        mission,
        "target_parameters",
    )

    if "communication_distance_m" in target_parameters:
        return float(target_parameters["communication_distance_m"])

    if "target_altitude_m" in target_parameters:
        return float(target_parameters["target_altitude_m"])

    return 0.0


async def register_communication_saga_worker(
    event_bus: EventBus,
) -> None:
    async def _publish_failure(
        *,
        event_bus: EventBus,
        envelope: EventEnvelope,
        subject: SagaSubject,
        reason: str,
    ) -> None:
        payload = {
            "saga_id": envelope.payload["saga_id"],
            "mission_id": envelope.payload["mission_id"],
            "reason": reason,
        }

        result = EventEnvelope.create(
            event_type=subject.value,
            source=settings.service_name,
            correlation_id=envelope.correlation_id,
            causation_id=envelope.event_id,
            payload=payload,
        )

        await event_bus.publish(
            subject=subject.value,
            envelope=result,
        )

    async def create_profile(
        envelope: EventEnvelope,
    ) -> None:
        try:
            mission_id = _require_uuid(
                envelope.payload,
                "mission_id",
            )

            mission = _require_dict(
                envelope.payload,
                "mission",
            )

            request = CommunicationProfileCreateRequest(
                mission_id=mission_id,
                distance_m=(_communication_distance(mission)),
                additional_latency_ms=0.0,
                packet_loss_percent=0.0,
                signal_status=(SignalStatus.AVAILABLE),
            )

            async with SessionFactory() as session:
                profile = await CommunicationService(session).create_profile(request)

            await publish_communication_status(
                event_bus=event_bus,
                profile=profile,
                causation_id=envelope.event_id,
            )

            payload = {
                "saga_id": envelope.payload["saga_id"],
                "mission_id": str(mission_id),
                "communication_profile_id": str(profile.id),
            }

            result = EventEnvelope.create(
                event_type=(SagaSubject.COMMUNICATION_PROFILE_CREATED.value),
                source=settings.service_name,
                correlation_id=(envelope.correlation_id),
                causation_id=(envelope.event_id),
                payload=payload,
            )

            await event_bus.publish(
                subject=(SagaSubject.COMMUNICATION_PROFILE_CREATED.value),
                envelope=result,
            )
        except Exception as error:
            await _publish_failure(
                event_bus=event_bus,
                envelope=envelope,
                subject=(SagaSubject.COMMUNICATION_PROFILE_REJECTED),
                reason=str(error),
            )
            return

    async def remove_profile(
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        async with SessionFactory() as session:
            await CommunicationService(session).remove_profile(mission_id)

        result = EventEnvelope.create(
            event_type=(SagaSubject.COMMUNICATION_PROFILE_REMOVED.value),
            source=settings.service_name,
            correlation_id=(envelope.correlation_id),
            causation_id=envelope.event_id,
            payload={
                "saga_id": envelope.payload["saga_id"],
                "mission_id": str(mission_id),
            },
        )

        await event_bus.publish(
            subject=(SagaSubject.COMMUNICATION_PROFILE_REMOVED.value),
            envelope=result,
        )

    async def _run_once(
        envelope: EventEnvelope,
        handler: Callable[
            [EventEnvelope],
            Awaitable[None],
        ],
    ) -> None:
        async with SessionFactory() as session:
            service = IdempotencyService(session)

            if await service.was_processed(envelope):
                return

        await handler(envelope)

        async with SessionFactory() as session:
            await IdempotencyService(session).mark_processed(envelope)

    async def create_profile_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(envelope, create_profile)

    async def remove_profile_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(envelope, remove_profile)

    await event_bus.subscribe(
        subject=(SagaSubject.COMMUNICATION_PROFILE_REQUESTED.value),
        durable_name=("communication-saga-profile-worker"),
        handler=create_profile_handler,
    )

    await event_bus.subscribe(
        subject=(SagaSubject.COMMUNICATION_PROFILE_REMOVE_REQUESTED.value),
        durable_name=("communication-saga-remove-worker"),
        handler=remove_profile_handler,
    )
