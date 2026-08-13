from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    SagaSubject,
)

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.schemas.trajectory import TrajectoryPlanRequest
from app.services.trajectory_service import TrajectoryService

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


def _require_float(
    payload: dict[str, Any],
    field: str,
) -> float:
    value = payload.get(field)

    if value is None:
        raise ValueError(f"Event payload is missing '{field}'.")

    return float(value)


def _optional_float(
    payload: dict[str, Any],
    field: str,
    *,
    default: float,
) -> float:
    value = payload.get(field, default)

    return float(value)


def _parse_departure_time(
    mission: dict[str, Any],
) -> datetime:
    value = mission.get("planned_launch_time")

    if value is None:
        return datetime.now(UTC)

    departure_time = datetime.fromisoformat(str(value))

    if departure_time.tzinfo is None:
        raise ValueError("planned_launch_time must include timezone information.")

    return departure_time


async def register_trajectory_saga_worker(
    event_bus: EventBus,
) -> None:
    async def plan_trajectory(
        envelope: EventEnvelope,
    ) -> None:
        mission = _require_dict(
            envelope.payload,
            "mission",
        )

        vehicle = _require_dict(
            envelope.payload,
            "vehicle",
        )

        target_parameters = _require_dict(
            mission,
            "target_parameters",
        )

        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        request = TrajectoryPlanRequest(
            mission_id=mission_id,
            initial_altitude_m=_require_float(
                target_parameters,
                "initial_altitude_m",
            ),
            target_altitude_m=_require_float(
                target_parameters,
                "target_altitude_m",
            ),
            total_mass_kg=_require_float(
                vehicle,
                "initial_mass_kg",
            ),
            available_propellant_kg=_require_float(
                vehicle,
                "propellant_capacity_kg",
            ),
            engine_specific_impulse_s=_require_float(
                vehicle,
                "engine_specific_impulse_s",
            ),
            departure_time=(_parse_departure_time(mission)),
            minimum_propellant_reserve_percent=_optional_float(
                target_parameters,
                "minimum_propellant_reserve_percent",
                default=10.0,
            ),
        )

        async with SessionFactory() as session:
            trajectory = await TrajectoryService(session).plan(request)

        trajectory_payload = {
            "id": str(trajectory.id),
            "departure_time": (trajectory.departure_time.isoformat()),
            "arrival_time": (trajectory.arrival_time.isoformat()),
            "initial_total_mass_kg": (trajectory.initial_state_vector["total_mass_kg"]),
            "initial_state_vector": (trajectory.initial_state_vector),
            "target_state_vector": (trajectory.target_state_vector),
            "required_delta_v_m_s": (trajectory.required_delta_v_m_s),
            "estimated_propellant_kg": (trajectory.estimated_propellant_kg),
            "propellant_reserve_percent": (trajectory.propellant_reserve_percent),
            "minimum_propellant_reserve_percent": (request.minimum_propellant_reserve_percent),
            "safety_margin_percent": (trajectory.safety_margin_percent),
            "window_score": (trajectory.window_score),
            "status": trajectory.status.value,
            "maneuvers": [
                {
                    "id": str(maneuver.id),
                    "sequence": maneuver.sequence,
                    "maneuver_type": (maneuver.maneuver_type.value),
                    "delta_v_m_s": (maneuver.delta_v_m_s),
                    "planned_offset_s": (maneuver.planned_offset_s),
                }
                for maneuver in trajectory.maneuvers
            ],
        }

        payload = {
            "saga_id": envelope.payload["saga_id"],
            "mission_id": str(mission_id),
            "trajectory_plan_id": str(trajectory.id),
            "trajectory": trajectory_payload,
        }

        result = EventEnvelope.create(
            event_type=(SagaSubject.TRAJECTORY_PLAN_CREATED.value),
            source=settings.service_name,
            correlation_id=(envelope.correlation_id),
            causation_id=(envelope.event_id),
            payload=payload,
        )

        await event_bus.publish(
            subject=(SagaSubject.TRAJECTORY_PLAN_CREATED.value),
            envelope=result,
        )

    await event_bus.subscribe(
        subject=(SagaSubject.TRAJECTORY_PLAN_REQUESTED.value),
        durable_name=("trajectory-saga-planning-worker"),
        handler=plan_trajectory,
    )
