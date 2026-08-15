from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain.enums import MissionEventType, MissionStatus
from app.domain.exceptions import InvalidMissionTransitionError, MissionNotFoundError
from app.domain.transitions import can_transition
from app.models.mission import Mission
from app.models.mission_event import MissionEvent
from app.repositories.mission_repository import MissionRepository
from app.schemas.mission import MissionCreate


class MissionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = MissionRepository(session)
        self._source = get_settings().service_name

    async def create(self, data: MissionCreate) -> Mission:
        mission = Mission(**data.model_dump(), status=MissionStatus.DRAFT)
        self._repository.add(mission)
        await self._session.flush()
        self._repository.add_event(
            MissionEvent(
                mission_id=mission.id,
                event_type=MissionEventType.MISSION_CREATED,
                source=self._source,
                payload={"status": MissionStatus.DRAFT},
            )
        )
        await self._session.commit()
        await self._session.refresh(mission)
        return mission

    async def get(self, mission_id: UUID) -> Mission:
        mission = await self._repository.get_by_id(mission_id)
        if mission is None:
            raise MissionNotFoundError(mission_id)
        return mission

    async def list(self, *, limit: int, offset: int) -> tuple[Sequence[Mission], int]:
        return (
            await self._repository.list(limit=limit, offset=offset),
            await self._repository.count(),
        )

    async def prepare(self, mission_id: UUID) -> Mission:
        return await self._transition(
            mission_id,
            MissionStatus.PREPARING,
            MissionEventType.PREPARATION_REQUESTED,
        )

    async def launch(self, mission_id: UUID) -> Mission:
        return await self._transition(
            mission_id,
            MissionStatus.IN_PROGRESS,
            MissionEventType.MISSION_STARTED,
            started_at=datetime.now(UTC),
        )

    async def abort(self, mission_id: UUID) -> Mission:
        return await self._transition(
            mission_id,
            MissionStatus.ABORTING,
            MissionEventType.ABORT_REQUESTED,
        )

    async def complete_abort(
        self,
        mission_id: UUID,
    ) -> Mission:
        return await self._transition(
            mission_id,
            MissionStatus.ABORTED,
            MissionEventType.MISSION_ABORTED,
            completed_at=datetime.now(UTC),
        )

    async def fail_abort(
        self,
        mission_id: UUID,
        *,
        reason: str,
    ) -> Mission:
        return await self._transition(
            mission_id,
            MissionStatus.FAILED,
            MissionEventType.MISSION_FAILED,
            completed_at=datetime.now(UTC),
            failure_reason=reason,
        )

    async def timeline(self, mission_id: UUID) -> Sequence[MissionEvent]:
        await self.get(mission_id)
        return await self._repository.timeline(mission_id)

    async def _transition(
        self,
        mission_id: UUID,
        target_status: MissionStatus,
        event_type: MissionEventType,
        *,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        failure_reason: str | None = None,
    ) -> Mission:
        mission = await self._repository.get_by_id(mission_id, for_update=True)
        if mission is None:
            raise MissionNotFoundError(mission_id)

        previous_status = mission.status
        if not can_transition(previous_status, target_status):
            raise InvalidMissionTransitionError(mission.id, previous_status, target_status)

        mission.status = target_status
        mission.started_at = started_at or mission.started_at
        mission.completed_at = completed_at or mission.completed_at
        mission.failure_reason = failure_reason

        self._repository.add_event(
            MissionEvent(
                mission_id=mission.id,
                event_type=event_type,
                source=self._source,
                payload={
                    "previous_status": previous_status,
                    "new_status": target_status,
                },
            )
        )
        await self._session.commit()
        await self._session.refresh(mission)
        return mission
