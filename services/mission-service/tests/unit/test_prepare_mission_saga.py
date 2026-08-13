from typing import Any
from uuid import uuid4

import pytest
from smc_messaging import EventEnvelope
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import (
    MissionStatus,
    MissionType,
)
from app.schemas.mission import MissionCreate
from app.services.mission_service import (
    MissionService,
)
from app.services.prepare_mission_saga import (
    PrepareMissionSagaService,
)


class FakePublisher:
    def __init__(self) -> None:
        self.published: list[tuple[str, EventEnvelope]] = []

    async def publish(
        self,
        *,
        subject: str,
        envelope: EventEnvelope,
    ) -> None:
        self.published.append((subject, envelope))


def _mission_request() -> MissionCreate:
    return MissionCreate(
        name="LEO Saga Test",
        mission_type=MissionType.LEO,
        vehicle_id=uuid4(),
        crew_count=2,
        target_type="LEO_ORBIT",
        target_parameters={
            "initial_altitude_m": 400_000.0,
            "target_altitude_m": 500_000.0,
        },
        simulation_speed=10,
    )


@pytest.mark.asyncio
async def test_start_prepare_saga_publishes_vehicle_reservation(
    session: AsyncSession,
) -> None:
    mission = await MissionService(session).create(_mission_request())

    publisher = FakePublisher()

    result = await PrepareMissionSagaService(
        session,
        publisher,
    ).start(mission.id)

    assert result.status is MissionStatus.PREPARING

    assert len(publisher.published) == 1

    subject, envelope = publisher.published[0]

    assert subject == "vehicle.reserve.requested"

    assert envelope.payload["mission_id"] == str(mission.id)

    assert envelope.payload["vehicle_id"] == str(mission.vehicle_id)


@pytest.mark.asyncio
async def test_vehicle_reserved_advances_to_trajectory_planning(
    session: AsyncSession,
) -> None:
    mission = await MissionService(session).create(_mission_request())

    publisher = FakePublisher()

    saga_service = PrepareMissionSagaService(
        session,
        publisher,
    )

    await saga_service.start(mission.id)

    start_event = publisher.published[0][1]

    saga_id = start_event.payload["saga_id"]

    vehicle_payload: dict[str, Any] = {
        "saga_id": saga_id,
        "mission_id": str(mission.id),
        "vehicle_id": str(mission.vehicle_id),
        "vehicle": {
            "engine_thrust_n": 100_000.0,
            "engine_specific_impulse_s": 320.0,
            "propellant_capacity_kg": 5_000.0,
        },
    }

    vehicle_event = EventEnvelope.create(
        event_type="vehicle.reserved",
        source="vehicle-service",
        correlation_id=saga_id,
        causation_id=start_event.event_id,
        payload=vehicle_payload,
    )

    await saga_service.handle_vehicle_reserved(vehicle_event)

    assert len(publisher.published) == 2

    subject, trajectory_event = publisher.published[1]

    assert subject == "trajectory.plan.requested"

    assert trajectory_event.payload["mission_id"] == str(mission.id)

    assert trajectory_event.payload["vehicle"] == vehicle_payload["vehicle"]
