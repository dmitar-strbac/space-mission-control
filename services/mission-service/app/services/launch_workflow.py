from uuid import UUID

from smc_messaging import (
    EventEnvelope,
    SimulationLifecycleSubject,
)

from app.core.config import get_settings
from app.messaging.publisher import EventPublisher
from app.models.mission import Mission
from app.services.mission_service import MissionService

settings = get_settings()


class LaunchWorkflowService:
    def __init__(
        self,
        missions: MissionService,
        publisher: EventPublisher,
    ) -> None:
        self._missions = missions
        self._publisher = publisher

    async def launch(
        self,
        mission_id: UUID,
    ) -> Mission:
        mission = await self._missions.launch(mission_id)

        envelope = EventEnvelope.create(
            event_type=(SimulationLifecycleSubject.START_REQUESTED.value),
            source=settings.service_name,
            correlation_id=str(mission_id),
            payload={
                "mission_id": str(mission_id),
            },
        )

        try:
            await self._publisher.publish(
                subject=(SimulationLifecycleSubject.START_REQUESTED.value),
                envelope=envelope,
            )

        except Exception as error:
            await self._missions.fail(
                mission_id,
                reason=(f"Mission launch failed while requesting Flight Dynamics startup: {error}"),
            )

            raise

        return mission
