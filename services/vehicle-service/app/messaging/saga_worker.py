from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any
from uuid import UUID

from smc_messaging import (
    EventBus,
    EventEnvelope,
    SagaSubject,
)

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.domain.enums import MissionType
from app.schemas.saga import (
    FinalResourceValidationRequest,
    VehicleReservationRequest,
)
from app.services.idempotency_service import IdempotencyService
from app.services.spacecraft_service import SpacecraftService

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


def _float_value(
    payload: dict[str, Any],
    field: str,
    *,
    default: float = 0.0,
) -> float:
    value = payload.get(
        field,
        default,
    )

    return float(value)


async def register_vehicle_saga_worker(
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

    async def reserve_vehicle(
        envelope: EventEnvelope,
    ) -> None:
        try:
            mission = _require_dict(
                envelope.payload,
                "mission",
            )

            target_parameters = mission.get(
                "target_parameters",
                {},
            )

            if not isinstance(
                target_parameters,
                dict,
            ):
                target_parameters = {}

            request = VehicleReservationRequest(
                saga_id=_require_uuid(
                    envelope.payload,
                    "saga_id",
                ),
                mission_id=_require_uuid(
                    envelope.payload,
                    "mission_id",
                ),
                vehicle_id=_require_uuid(
                    envelope.payload,
                    "vehicle_id",
                ),
                mission_type=MissionType(str(mission["mission_type"])),
                crew_count=int(
                    mission.get(
                        "crew_count",
                        0,
                    )
                ),
                payload_mass_kg=_float_value(
                    target_parameters,
                    "payload_mass_kg",
                ),
            )

            async with SessionFactory() as session:
                spacecraft, validation = await SpacecraftService(session).reserve_for_mission(
                    request
                )

            payload = {
                "saga_id": str(request.saga_id),
                "mission_id": str(request.mission_id),
                "vehicle_id": str(spacecraft.id),
                "vehicle": {
                    "id": str(spacecraft.id),
                    "dry_mass_kg": (spacecraft.dry_mass_kg),
                    "payload_mass_kg": (request.payload_mass_kg),
                    "initial_mass_kg": (validation.initial_mass_kg),
                    "available_delta_v_m_s": (validation.available_delta_v_m_s),
                    "engine_thrust_n": (spacecraft.engine_thrust_n),
                    "engine_specific_impulse_s": (spacecraft.engine_specific_impulse_s),
                    "propellant_capacity_kg": (spacecraft.propellant_capacity_kg),
                    "oxygen_capacity_kg": (spacecraft.oxygen_capacity_kg),
                    "battery_capacity_kwh": (spacecraft.battery_capacity_kwh),
                    "max_acceleration_g": (spacecraft.max_acceleration_g),
                },
            }

            result = EventEnvelope.create(
                event_type=(SagaSubject.VEHICLE_RESERVED.value),
                source=settings.service_name,
                correlation_id=(envelope.correlation_id),
                causation_id=envelope.event_id,
                payload=payload,
            )

            await event_bus.publish(
                subject=(SagaSubject.VEHICLE_RESERVED.value),
                envelope=result,
            )
        except Exception as error:
            await _publish_failure(
                event_bus=event_bus,
                envelope=envelope,
                subject=(SagaSubject.VEHICLE_RESERVATION_REJECTED),
                reason=str(error),
            )
            return

    async def validate_resources(
        envelope: EventEnvelope,
    ) -> None:
        try:
            trajectory = _require_dict(
                envelope.payload,
                "trajectory",
            )

            departure_time = datetime.fromisoformat(str(trajectory["departure_time"]))

            arrival_time = datetime.fromisoformat(str(trajectory["arrival_time"]))

            duration_s = (arrival_time - departure_time).total_seconds()

            request = FinalResourceValidationRequest(
                saga_id=_require_uuid(
                    envelope.payload,
                    "saga_id",
                ),
                mission_id=_require_uuid(
                    envelope.payload,
                    "mission_id",
                ),
                vehicle_id=_require_uuid(
                    envelope.payload,
                    "vehicle_id",
                ),
                total_mass_kg=_float_value(
                    trajectory,
                    "initial_total_mass_kg",
                ),
                required_propellant_kg=_float_value(
                    trajectory,
                    "estimated_propellant_kg",
                ),
                minimum_propellant_reserve_percent=_float_value(
                    trajectory,
                    "minimum_propellant_reserve_percent",
                    default=10.0,
                ),
                mission_duration_s=duration_s,
                oxygen_consumption_rate_kg_s=_float_value(
                    trajectory,
                    "oxygen_consumption_rate_kg_s",
                ),
                power_consumption_kw=_float_value(
                    trajectory,
                    "power_consumption_kw",
                ),
            )

            async with SessionFactory() as session:
                service = SpacecraftService(session)

                validation = await service.validate_final_resources_for_mission(request)

                spacecraft = await service.get(request.vehicle_id)

            payload = {
                "saga_id": str(request.saga_id),
                "mission_id": str(request.mission_id),
                "vehicle_id": str(request.vehicle_id),
                "resources": {
                    "required_propellant_kg": (validation.required_propellant_kg),
                    "available_propellant_kg": (validation.available_propellant_kg),
                    "required_oxygen_kg": (validation.required_oxygen_kg),
                    "available_oxygen_kg": (validation.available_oxygen_kg),
                    "required_energy_kwh": (validation.required_energy_kwh),
                    "available_energy_kwh": (validation.available_energy_kwh),
                    "estimated_acceleration_g": (validation.estimated_acceleration_g),
                    "oxygen_capacity_kg": (spacecraft.oxygen_capacity_kg),
                    "battery_capacity_kwh": (spacecraft.battery_capacity_kwh),
                },
            }

            result = EventEnvelope.create(
                event_type=(SagaSubject.RESOURCES_VALIDATED.value),
                source=settings.service_name,
                correlation_id=(envelope.correlation_id),
                causation_id=envelope.event_id,
                payload=payload,
            )

            await event_bus.publish(
                subject=(SagaSubject.RESOURCES_VALIDATED.value),
                envelope=result,
            )
        except Exception as error:
            await _publish_failure(
                event_bus=event_bus,
                envelope=envelope,
                subject=(SagaSubject.RESOURCES_VALIDATION_REJECTED),
                reason=str(error),
            )
            return

    async def release_vehicle(
        envelope: EventEnvelope,
    ) -> None:
        mission_id = _require_uuid(
            envelope.payload,
            "mission_id",
        )

        async with SessionFactory() as session:
            await SpacecraftService(session).release_for_mission(mission_id)

        result = EventEnvelope.create(
            event_type=(SagaSubject.VEHICLE_RELEASED.value),
            source=settings.service_name,
            correlation_id=(envelope.correlation_id),
            causation_id=envelope.event_id,
            payload={
                "saga_id": envelope.payload["saga_id"],
                "mission_id": str(mission_id),
            },
        )

        await event_bus.publish(
            subject=(SagaSubject.VEHICLE_RELEASED.value),
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

    async def reserve_vehicle_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(envelope, reserve_vehicle)

    async def validate_resources_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(envelope, validate_resources)

    async def release_vehicle_handler(
        envelope: EventEnvelope,
    ) -> None:
        await _run_once(envelope, release_vehicle)

    await event_bus.subscribe(
        subject=(SagaSubject.VEHICLE_RESERVE_REQUESTED.value),
        durable_name=("vehicle-saga-reserve-worker"),
        handler=reserve_vehicle_handler,
    )

    await event_bus.subscribe(
        subject=(SagaSubject.RESOURCES_VALIDATION_REQUESTED.value),
        durable_name=("vehicle-saga-resource-validation-worker"),
        handler=validate_resources_handler,
    )

    await event_bus.subscribe(
        subject=(SagaSubject.VEHICLE_RELEASE_REQUESTED.value),
        durable_name=("vehicle-saga-release-worker"),
        handler=release_vehicle_handler,
    )
