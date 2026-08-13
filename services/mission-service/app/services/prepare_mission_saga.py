from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from smc_messaging import EventEnvelope, SagaSubject
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain.enums import (
    MissionEventType,
    MissionStatus,
    SagaStepType,
)
from app.domain.exceptions import (
    InvalidMissionTransitionError,
    MissionNotFoundError,
)
from app.domain.transitions import can_transition
from app.messaging.publisher import EventPublisher
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.repositories.mission_repository import (
    MissionRepository,
)
from app.services.saga_step_service import (
    SagaStepService,
)


class PrepareMissionSagaService:
    def __init__(
        self,
        session: AsyncSession,
        publisher: EventPublisher,
    ) -> None:
        self._session = session
        self._publisher = publisher

        self._missions = MissionRepository(session)
        self._steps = SagaStepService(session)

        self._source = get_settings().service_name

    async def start(
        self,
        mission_id: UUID,
    ) -> Mission:
        mission = await self._missions.get_by_id(
            mission_id,
            for_update=True,
        )

        if mission is None:
            raise MissionNotFoundError(mission_id)

        if not can_transition(
            mission.status,
            MissionStatus.PREPARING,
        ):
            raise InvalidMissionTransitionError(
                mission.id,
                mission.status,
                MissionStatus.PREPARING,
            )

        if mission.vehicle_id is None:
            raise ValueError("Mission must have an assigned vehicle before preparation can start.")

        saga_id = uuid4()

        await self._steps.create_prepare_steps(
            saga_id=saga_id,
            mission_id=mission.id,
        )

        previous_status = mission.status

        mission.status = MissionStatus.PREPARING
        mission.failure_reason = None

        self._missions.add_event(
            MissionEvent(
                mission_id=mission.id,
                event_type=(MissionEventType.PREPARATION_REQUESTED),
                source=self._source,
                payload={
                    "saga_id": str(saga_id),
                    "previous_status": (previous_status.value),
                    "new_status": (MissionStatus.PREPARING.value),
                },
            )
        )

        payload = self._build_vehicle_reservation_payload(
            saga_id=saga_id,
            mission=mission,
        )

        envelope = EventEnvelope.create(
            event_type=(SagaSubject.VEHICLE_RESERVE_REQUESTED.value),
            source=self._source,
            correlation_id=str(saga_id),
            payload=payload,
        )

        await self._steps.mark_in_progress(
            saga_id=saga_id,
            step_type=(SagaStepType.VEHICLE_RESERVATION),
            request_event_id=envelope.event_id,
            request_payload=payload,
        )

        await self._session.commit()
        await self._session.refresh(mission)

        await self._publisher.publish(
            subject=(SagaSubject.VEHICLE_RESERVE_REQUESTED.value),
            envelope=envelope,
        )

        return mission

    async def handle_vehicle_reserved(
        self,
        envelope: EventEnvelope,
    ) -> None:
        saga_id, mission_id = self._extract_context(envelope)

        await self._steps.mark_completed(
            saga_id=saga_id,
            step_type=(SagaStepType.VEHICLE_RESERVATION),
            result_event_id=envelope.event_id,
            result_payload=envelope.payload,
        )

        mission = await self._require_mission(mission_id)

        payload = {
            "saga_id": str(saga_id),
            "mission_id": str(mission_id),
            "vehicle_id": str(self._require_vehicle_id(mission)),
            "mission": (self._serialize_mission(mission)),
            "vehicle": envelope.payload.get(
                "vehicle",
                {},
            ),
        }

        await self._publish_next_step(
            saga_id=saga_id,
            step_type=(SagaStepType.TRAJECTORY_PLANNING),
            subject=(SagaSubject.TRAJECTORY_PLAN_REQUESTED),
            payload=payload,
            causation_id=envelope.event_id,
        )

    async def handle_trajectory_plan_created(
        self,
        envelope: EventEnvelope,
    ) -> None:
        saga_id, mission_id = self._extract_context(envelope)

        await self._steps.mark_completed(
            saga_id=saga_id,
            step_type=(SagaStepType.TRAJECTORY_PLANNING),
            result_event_id=envelope.event_id,
            result_payload=envelope.payload,
        )

        mission = await self._require_mission(mission_id)

        trajectory_plan_id = self._require_uuid_field(
            envelope.payload,
            "trajectory_plan_id",
        )

        payload = {
            "saga_id": str(saga_id),
            "mission_id": str(mission_id),
            "vehicle_id": str(self._require_vehicle_id(mission)),
            "trajectory_plan_id": str(trajectory_plan_id),
            "trajectory": envelope.payload.get(
                "trajectory",
                {},
            ),
        }

        await self._publish_next_step(
            saga_id=saga_id,
            step_type=(SagaStepType.RESOURCE_VALIDATION),
            subject=(SagaSubject.RESOURCES_VALIDATION_REQUESTED),
            payload=payload,
            causation_id=envelope.event_id,
        )

    async def handle_resources_validated(
        self,
        envelope: EventEnvelope,
    ) -> None:
        saga_id, mission_id = self._extract_context(envelope)

        await self._steps.mark_completed(
            saga_id=saga_id,
            step_type=(SagaStepType.RESOURCE_VALIDATION),
            result_event_id=envelope.event_id,
            result_payload=envelope.payload,
        )

        mission = await self._require_mission(mission_id)

        payload = {
            "saga_id": str(saga_id),
            "mission_id": str(mission_id),
            "mission": (self._serialize_mission(mission)),
        }

        await self._publish_next_step(
            saga_id=saga_id,
            step_type=(SagaStepType.COMMUNICATION_PROFILE),
            subject=(SagaSubject.COMMUNICATION_PROFILE_REQUESTED),
            payload=payload,
            causation_id=envelope.event_id,
        )

    async def handle_communication_profile_created(
        self,
        envelope: EventEnvelope,
    ) -> None:
        saga_id, mission_id = self._extract_context(envelope)

        await self._steps.mark_completed(
            saga_id=saga_id,
            step_type=(SagaStepType.COMMUNICATION_PROFILE),
            result_event_id=envelope.event_id,
            result_payload=envelope.payload,
        )

        mission = await self._require_mission(mission_id)

        vehicle_result = await self._steps.get_result_payload(
            saga_id=saga_id,
            step_type=(SagaStepType.VEHICLE_RESERVATION),
        )

        trajectory_result = await self._steps.get_result_payload(
            saga_id=saga_id,
            step_type=(SagaStepType.TRAJECTORY_PLANNING),
        )

        if vehicle_result is None:
            raise RuntimeError("Vehicle reservation result is missing.")

        if trajectory_result is None:
            raise RuntimeError("Trajectory planning result is missing.")

        trajectory_plan_id = self._require_uuid_field(
            trajectory_result,
            "trajectory_plan_id",
        )

        payload = {
            "saga_id": str(saga_id),
            "mission_id": str(mission_id),
            "vehicle_id": str(self._require_vehicle_id(mission)),
            "trajectory_plan_id": str(trajectory_plan_id),
            "mission": (self._serialize_mission(mission)),
            "vehicle": vehicle_result.get(
                "vehicle",
                {},
            ),
            "trajectory": trajectory_result.get(
                "trajectory",
                {},
            ),
        }

        await self._publish_next_step(
            saga_id=saga_id,
            step_type=(SagaStepType.SIMULATION_INITIALIZATION),
            subject=(SagaSubject.SIMULATION_INITIALIZE_REQUESTED),
            payload=payload,
            causation_id=envelope.event_id,
        )

    async def handle_simulation_initialized(
        self,
        envelope: EventEnvelope,
    ) -> Mission:
        saga_id, mission_id = self._extract_context(envelope)

        await self._steps.mark_completed(
            saga_id=saga_id,
            step_type=(SagaStepType.SIMULATION_INITIALIZATION),
            result_event_id=envelope.event_id,
            result_payload=envelope.payload,
        )

        mission = await self._missions.get_by_id(
            mission_id,
            for_update=True,
        )

        if mission is None:
            raise MissionNotFoundError(mission_id)

        if not can_transition(
            mission.status,
            MissionStatus.READY,
        ):
            raise InvalidMissionTransitionError(
                mission.id,
                mission.status,
                MissionStatus.READY,
            )

        previous_status = mission.status

        mission.status = MissionStatus.READY
        mission.failure_reason = None

        self._missions.add_event(
            MissionEvent(
                mission_id=mission.id,
                event_type=(MissionEventType.STATUS_CHANGED),
                source=self._source,
                payload={
                    "saga_id": str(saga_id),
                    "previous_status": (previous_status.value),
                    "new_status": (MissionStatus.READY.value),
                    "reason": ("Prepare Mission Saga completed."),
                },
            )
        )

        await self._session.commit()
        await self._session.refresh(mission)

        ready_payload = {
            "saga_id": str(saga_id),
            "mission_id": str(mission.id),
            "status": MissionStatus.READY.value,
        }

        ready_event = EventEnvelope.create(
            event_type=(SagaSubject.MISSION_READY.value),
            source=self._source,
            correlation_id=str(saga_id),
            causation_id=envelope.event_id,
            payload=ready_payload,
        )

        await self._publisher.publish(
            subject=SagaSubject.MISSION_READY.value,
            envelope=ready_event,
        )

        return mission

    async def _publish_next_step(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
        subject: SagaSubject,
        payload: dict[str, Any],
        causation_id: UUID,
    ) -> None:
        envelope = EventEnvelope.create(
            event_type=subject.value,
            source=self._source,
            correlation_id=str(saga_id),
            causation_id=causation_id,
            payload=payload,
        )

        await self._steps.mark_in_progress(
            saga_id=saga_id,
            step_type=step_type,
            request_event_id=envelope.event_id,
            request_payload=payload,
        )

        await self._session.commit()

        await self._publisher.publish(
            subject=subject.value,
            envelope=envelope,
        )

    async def _require_mission(
        self,
        mission_id: UUID,
    ) -> Mission:
        mission = await self._missions.get_by_id(mission_id)

        if mission is None:
            raise MissionNotFoundError(mission_id)

        return mission

    @staticmethod
    def _extract_context(
        envelope: EventEnvelope,
    ) -> tuple[UUID, UUID]:
        saga_id = PrepareMissionSagaService._require_uuid_field(
            envelope.payload,
            "saga_id",
        )

        mission_id = PrepareMissionSagaService._require_uuid_field(
            envelope.payload,
            "mission_id",
        )

        return saga_id, mission_id

    @staticmethod
    def _require_uuid_field(
        payload: dict[str, Any],
        field: str,
    ) -> UUID:
        value = payload.get(field)

        if value is None:
            raise ValueError(f"Event payload is missing '{field}'.")

        return UUID(str(value))

    @staticmethod
    def _require_vehicle_id(
        mission: Mission,
    ) -> UUID:
        if mission.vehicle_id is None:
            raise ValueError("Mission does not have an assigned vehicle.")

        return mission.vehicle_id

    @staticmethod
    def _serialize_mission(
        mission: Mission,
    ) -> dict[str, Any]:
        planned_launch_time: datetime | None = mission.planned_launch_time

        return {
            "id": str(mission.id),
            "mission_type": (mission.mission_type.value),
            "crew_count": mission.crew_count,
            "target_type": mission.target_type,
            "target_parameters": (mission.target_parameters),
            "planned_launch_time": (
                planned_launch_time.isoformat() if planned_launch_time is not None else None
            ),
            "simulation_speed": (mission.simulation_speed),
        }

    def _build_vehicle_reservation_payload(
        self,
        *,
        saga_id: UUID,
        mission: Mission,
    ) -> dict[str, Any]:
        vehicle_id = self._require_vehicle_id(mission)

        return {
            "saga_id": str(saga_id),
            "mission_id": str(mission.id),
            "vehicle_id": str(vehicle_id),
            "mission": (self._serialize_mission(mission)),
        }
