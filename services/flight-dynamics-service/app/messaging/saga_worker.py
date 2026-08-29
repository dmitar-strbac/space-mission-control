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
from app.domain.enums import ManeuverType
from app.schemas.simulation import (
    PlannedManeuverSchema,
    SimulationInitializeRequest,
    StateVectorSchema,
)
from app.services.idempotency_service import IdempotencyService
from app.services.simulation_runtime import simulation_runtime_manager
from app.services.simulation_service import SimulationService

settings = get_settings()


def _require_dict(
    payload: dict[str, Any],
    field: str,
) -> dict[str, Any]:
    value = payload.get(field)

    if not isinstance(value, dict):
        raise ValueError(f"Event payload field '{field}' must be an object.")

    return value


def _require_list(
    payload: dict[str, Any],
    field: str,
) -> list[Any]:
    value = payload.get(field)

    if not isinstance(value, list):
        raise ValueError(f"Event payload field '{field}' must be a list.")

    return value


def _require_uuid(
    payload: dict[str, Any],
    field: str,
) -> UUID:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return UUID(str(value))


def _float_value(
    payload: dict[str, Any],
    field: str,
    *,
    default: float = 0.0,
) -> float:
    return float(
        payload.get(
            field,
            default,
        )
    )


async def register_flight_dynamics_saga_worker(
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

    async def initialize_simulation(
        envelope: EventEnvelope,
    ) -> None:
        try:
            mission = _require_dict(
                envelope.payload,
                "mission",
            )

            vehicle = _require_dict(
                envelope.payload,
                "vehicle",
            )

            trajectory = _require_dict(
                envelope.payload,
                "trajectory",
            )

            initial_state_raw = _require_dict(
                trajectory,
                "initial_state_vector",
            )

            maneuvers_raw = _require_list(
                trajectory,
                "maneuvers",
            )

            planned_maneuvers: list[PlannedManeuverSchema] = []

            for raw in maneuvers_raw:
                if not isinstance(raw, dict):
                    raise ValueError("Trajectory maneuver must be an object.")

                planned_maneuvers.append(
                    PlannedManeuverSchema(
                        id=UUID(str(raw["id"])),
                        sequence=int(raw["sequence"]),
                        maneuver_type=ManeuverType(str(raw["maneuver_type"])),
                        delta_v_m_s=float(raw["delta_v_m_s"]),
                        planned_offset_s=float(raw["planned_offset_s"]),
                    )
                )

            mission_id = _require_uuid(
                envelope.payload,
                "mission_id",
            )

            resources = _require_dict(
                envelope.payload,
                "resources",
            )

            request = SimulationInitializeRequest(
                mission_id=mission_id,
                trajectory_plan_id=_require_uuid(
                    envelope.payload,
                    "trajectory_plan_id",
                ),
                vehicle_id=_require_uuid(
                    envelope.payload,
                    "vehicle_id",
                ),
                initial_state_vector=(StateVectorSchema.model_validate(initial_state_raw)),
                planned_maneuvers=(planned_maneuvers),
                engine_thrust_n=_float_value(
                    vehicle,
                    "engine_thrust_n",
                ),
                engine_specific_impulse_s=_float_value(
                    vehicle,
                    "engine_specific_impulse_s",
                ),
                oxygen_kg=float(
                    resources.get(
                        "available_oxygen_kg",
                        vehicle.get(
                            "oxygen_capacity_kg",
                            0.0,
                        ),
                    )
                ),
                oxygen_consumption_rate_kg_s=_float_value(
                    mission,
                    "oxygen_consumption_rate_kg_s",
                ),
                power_consumption_kw=_float_value(
                    mission,
                    "power_consumption_kw",
                ),
                simulation_speed=int(
                    mission.get(
                        "simulation_speed",
                        1,
                    )
                ),
            )

            async with SessionFactory() as session:
                simulation = await SimulationService(session).initialize(request)

            payload = {
                "saga_id": envelope.payload["saga_id"],
                "mission_id": str(mission_id),
                "simulation_session_id": str(simulation.id),
            }

            result = EventEnvelope.create(
                event_type=(SagaSubject.SIMULATION_INITIALIZED.value),
                source=settings.service_name,
                correlation_id=(envelope.correlation_id),
                causation_id=(envelope.event_id),
                payload=payload,
            )

            await event_bus.publish(
                subject=(SagaSubject.SIMULATION_INITIALIZED.value),
                envelope=result,
            )
        except Exception as error:
            await _publish_failure(
                event_bus=event_bus,
                envelope=envelope,
                subject=(SagaSubject.SIMULATION_INITIALIZATION_REJECTED),
                reason=str(error),
            )
            return

    async def cleanup_simulation(
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        await simulation_runtime_manager.stop(
            mission_id,
        )

        async with SessionFactory() as session:
            await SimulationService(session).cleanup(mission_id)

        result = EventEnvelope.create(
            event_type=(SagaSubject.SIMULATION_CLEANED.value),
            source=settings.service_name,
            correlation_id=(envelope.correlation_id),
            causation_id=envelope.event_id,
            payload={
                "saga_id": envelope.payload["saga_id"],
                "mission_id": str(mission_id),
            },
        )

        await event_bus.publish(
            subject=(SagaSubject.SIMULATION_CLEANED.value),
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

    async def initialize_simulation_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(envelope, initialize_simulation)

    async def cleanup_simulation_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(envelope, cleanup_simulation)

    await event_bus.subscribe(
        subject=(SagaSubject.SIMULATION_INITIALIZE_REQUESTED.value),
        durable_name=("flight-dynamics-saga-initialize-worker"),
        handler=initialize_simulation_handler,
    )

    await event_bus.subscribe(
        subject=(SagaSubject.SIMULATION_CLEANUP_REQUESTED.value),
        durable_name=("flight-dynamics-saga-cleanup-worker"),
        handler=cleanup_simulation_handler,
    )
