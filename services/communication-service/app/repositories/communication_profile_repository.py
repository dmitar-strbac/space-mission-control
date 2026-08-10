from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communication_profile import CommunicationProfile


class CommunicationProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(
        self,
        profile: CommunicationProfile,
    ) -> None:
        self._session.add(profile)

    async def get_by_mission_id(
        self,
        mission_id: UUID,
        *,
        for_update: bool = False,
    ) -> CommunicationProfile | None:
        statement = select(CommunicationProfile).where(
            CommunicationProfile.mission_id == mission_id
        )

        if for_update:
            statement = statement.with_for_update()

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()
