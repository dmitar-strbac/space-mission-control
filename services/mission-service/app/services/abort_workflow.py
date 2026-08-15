from uuid import UUID

from smc_messaging import (
    AbortSubject,
    EventEnvelope,
)

from app.core.config import get_settings
from app.domain.enums import MissionStatus
from app.messaging.publisher import EventPublisher
from app.models.mission import Mission
from app.services.mission_service import MissionService

settings = get_settings()


class AbortWorkflowService:
    def __init__(
        self,
        mission_service: MissionService,
        publisher: EventPublisher,
    ) -> None:
        self._missions = mission_service
        self._publisher = publisher

    async def request_abort(
        self,
        mission_id: UUID,
        *,
        reason: str,
        causation_id: UUID | str | None = None,
    ) -> Mission:
        mission = await self._missions.get(mission_id)

        if mission.status is MissionStatus.ABORTED:
            return mission

        if mission.status is MissionStatus.ABORTING:
            return mission

        mission = await self._missions.abort(mission_id)

        envelope = EventEnvelope.create(
            event_type=(AbortSubject.MISSION_ABORT_REQUESTED.value),
            source=settings.service_name,
            correlation_id=str(mission_id),
            causation_id=causation_id,
            payload={
                "mission_id": str(mission_id),
                "reason": reason,
            },
        )

        await self._publisher.publish(
            subject=(AbortSubject.MISSION_ABORT_REQUESTED.value),
            envelope=envelope,
        )

        return mission

    async def complete_abort(
        self,
        mission_id: UUID,
    ) -> Mission:
        return await self._missions.complete_abort(mission_id)

    async def fail_abort(
        self,
        mission_id: UUID,
        *,
        reason: str,
    ) -> Mission:
        mission = await self._missions.get(mission_id)

        if mission.status is not MissionStatus.ABORTING:
            return mission

        return await self._missions.fail_abort(
            mission_id,
            reason=reason,
        )
