from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mission import Mission
from app.models.mission_event import MissionEvent


class MissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, mission: Mission) -> None:
        self._session.add(mission)

    def add_event(self, event: MissionEvent) -> None:
        self._session.add(event)

    async def get_by_id(
        self,
        mission_id: UUID,
        *,
        for_update: bool = False,
    ) -> Mission | None:
        statement = select(Mission).where(Mission.id == mission_id)

        if for_update:
            statement = statement.with_for_update()

        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def list(self, *, limit: int, offset: int) -> Sequence[Mission]:
        result = await self._session.scalars(
            select(Mission).order_by(Mission.created_at.desc()).limit(limit).offset(offset)
        )
        return result.all()

    async def count(self) -> int:
        return int(await self._session.scalar(select(func.count()).select_from(Mission)) or 0)

    async def timeline(self, mission_id: UUID) -> Sequence[MissionEvent]:
        result = await self._session.scalars(
            select(MissionEvent)
            .where(MissionEvent.mission_id == mission_id)
            .order_by(MissionEvent.occurred_at.asc(), MissionEvent.id.asc())
        )
        return result.all()
