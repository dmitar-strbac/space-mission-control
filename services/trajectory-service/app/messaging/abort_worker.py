from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from smc_messaging import (
    AbortSubject,
    EventBus,
    EventEnvelope,
)

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.schemas.trajectory import (
    SafeReturnPlanRequest,
    StateVectorSchema,
)
from app.services.idempotency_service import IdempotencyService
from app.services.trajectory_service import TrajectoryService

settings = get_settings()


def _require_uuid(
    payload: dict[str, Any],
    field: str,
) -> UUID:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return UUID(str(value))


def _require_dict(
    payload: dict[str, Any],
    field: str,
) -> dict[str, Any]:
    value = payload.get(field)

    if not isinstance(value, dict):
        raise ValueError(f"Event payload field '{field}' must be an object.")

    return value


async def register_abort_worker(
    event_bus: EventBus,
) -> None:
    async def process_abort(
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        try:
            state = _require_dict(
                envelope.payload,
                "state_vector",
            )

            async with SessionFactory() as session:
                idempotency = IdempotencyService(session)

                if await idempotency.was_processed(envelope):
                    return

                request = SafeReturnPlanRequest(
                    mission_id=mission_id,
                    current_state_vector=(StateVectorSchema.model_validate(state)),
                    engine_specific_impulse_s=float(envelope.payload["engine_specific_impulse_s"]),
                    departure_time=(datetime.now(UTC)),
                )

                trajectory = await TrajectoryService(session).plan_safe_return(request)

                await idempotency.mark_processed(envelope)

            maneuver = trajectory.maneuvers[0]

            result = EventEnvelope.create(
                event_type=(AbortSubject.TRAJECTORY_SAFE_RETURN_CREATED.value),
                source=settings.service_name,
                correlation_id=(envelope.correlation_id),
                causation_id=(envelope.event_id),
                payload={
                    "mission_id": str(mission_id),
                    "trajectory_plan_id": str(trajectory.id),
                    "required_delta_v_m_s": (trajectory.required_delta_v_m_s),
                    "estimated_propellant_kg": (trajectory.estimated_propellant_kg),
                    "maneuver": {
                        "id": str(maneuver.id),
                        "maneuver_type": (maneuver.maneuver_type.value),
                        "delta_v_m_s": (maneuver.delta_v_m_s),
                    },
                },
            )

            await event_bus.publish(
                subject=(AbortSubject.TRAJECTORY_SAFE_RETURN_CREATED.value),
                envelope=result,
            )

        except Exception as error:
            result = EventEnvelope.create(
                event_type=(AbortSubject.ABORT_FAILED.value),
                source=settings.service_name,
                correlation_id=(envelope.correlation_id),
                causation_id=(envelope.event_id),
                payload={
                    "mission_id": str(mission_id),
                    "failed_service": (settings.service_name),
                    "reason": str(error),
                },
            )

            await event_bus.publish(
                subject=(AbortSubject.ABORT_FAILED.value),
                envelope=result,
            )

    await event_bus.subscribe(
        subject=(AbortSubject.SIMULATION_ABORT_STARTED.value),
        durable_name=("trajectory-safe-return-worker"),
        handler=process_abort,
    )
