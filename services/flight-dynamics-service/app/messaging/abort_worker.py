from typing import Any
from uuid import UUID

from smc_messaging import (
    AbortSubject,
    EventBus,
    EventEnvelope,
)

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.services.idempotency_service import IdempotencyService
from app.services.simulation_service import SimulationService

settings = get_settings()


def _require_uuid(
    payload: dict[str, Any],
    field: str,
) -> UUID:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return UUID(str(value))


async def _publish(
    *,
    event_bus: EventBus,
    source_event: EventEnvelope,
    subject: AbortSubject,
    payload: dict[str, object],
) -> None:
    result = EventEnvelope.create(
        event_type=subject.value,
        source=settings.service_name,
        correlation_id=(source_event.correlation_id),
        causation_id=source_event.event_id,
        payload=payload,
    )

    await event_bus.publish(
        subject=subject.value,
        envelope=result,
    )


async def register_abort_worker(
    event_bus: EventBus,
) -> None:
    async def command_abort_executed(
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        try:
            async with SessionFactory() as session:
                idempotency = IdempotencyService(session)

                if await idempotency.was_processed(envelope):
                    return

                simulation, runtime = await SimulationService(session).begin_abort(mission_id)

                await idempotency.mark_processed(envelope)

            await _publish(
                event_bus=event_bus,
                source_event=envelope,
                subject=(AbortSubject.SIMULATION_ABORT_STARTED),
                payload={
                    "mission_id": str(mission_id),
                    "simulation_session_id": str(simulation.id),
                    "state_vector": {
                        "position": {
                            "x": (runtime.state.position.x),
                            "y": (runtime.state.position.y),
                        },
                        "velocity": {
                            "x": (runtime.state.velocity.x),
                            "y": (runtime.state.velocity.y),
                        },
                        "total_mass_kg": (runtime.state.total_mass_kg),
                        "propellant_mass_kg": (runtime.state.propellant_mass_kg),
                        "elapsed_time_s": (runtime.state.elapsed_time_s),
                    },
                    "engine_specific_impulse_s": (simulation.engine_specific_impulse_s),
                },
            )

        except Exception as error:
            await _publish(
                event_bus=event_bus,
                source_event=envelope,
                subject=(AbortSubject.ABORT_FAILED),
                payload={
                    "mission_id": str(mission_id),
                    "failed_service": (settings.service_name),
                    "reason": str(error),
                },
            )

    async def safe_return_created(
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        maneuver = envelope.payload.get("maneuver")

        if not isinstance(maneuver, dict):
            raise ValueError("Abort trajectory payload is missing maneuver data.")

        try:
            async with SessionFactory() as session:
                idempotency = IdempotencyService(session)

                if await idempotency.was_processed(envelope):
                    return

                runtime = await SimulationService(session).execute_abort_maneuver(
                    mission_id,
                    maneuver_id=UUID(str(maneuver["id"])),
                    delta_v_m_s=float(maneuver["delta_v_m_s"]),
                )

                await idempotency.mark_processed(envelope)

            await _publish(
                event_bus=event_bus,
                source_event=envelope,
                subject=(AbortSubject.SIMULATION_ABORT_COMPLETED),
                payload={
                    "mission_id": str(mission_id),
                    "final_state_vector": {
                        "position": {
                            "x": (runtime.state.position.x),
                            "y": (runtime.state.position.y),
                        },
                        "velocity": {
                            "x": (runtime.state.velocity.x),
                            "y": (runtime.state.velocity.y),
                        },
                        "total_mass_kg": (runtime.state.total_mass_kg),
                        "propellant_mass_kg": (runtime.state.propellant_mass_kg),
                        "elapsed_time_s": (runtime.state.elapsed_time_s),
                    },
                },
            )

        except Exception as error:
            await _publish(
                event_bus=event_bus,
                source_event=envelope,
                subject=(AbortSubject.ABORT_FAILED),
                payload={
                    "mission_id": str(mission_id),
                    "failed_service": (settings.service_name),
                    "reason": str(error),
                },
            )

    await event_bus.subscribe(
        subject=(AbortSubject.COMMAND_ABORT_EXECUTED.value),
        durable_name=("flight-dynamics-abort-command-worker"),
        handler=command_abort_executed,
    )

    await event_bus.subscribe(
        subject=(AbortSubject.TRAJECTORY_SAFE_RETURN_CREATED.value),
        durable_name=("flight-dynamics-safe-return-worker"),
        handler=safe_return_created,
    )
