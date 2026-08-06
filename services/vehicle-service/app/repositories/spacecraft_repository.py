from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spacecraft import Spacecraft


class SpacecraftRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, spacecraft: Spacecraft) -> None:
        self._session.add(spacecraft)

    async def get_by_id(
        self,
        spacecraft_id: UUID,
    ) -> Spacecraft | None:
        statement = select(Spacecraft).where(Spacecraft.id == spacecraft_id)
        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Spacecraft | None:
        statement = select(Spacecraft).where(func.lower(Spacecraft.name) == name.lower())
        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        offset: int,
        limit: int,
    ) -> list[Spacecraft]:
        statement = (
            select(Spacecraft).order_by(Spacecraft.created_at.desc()).offset(offset).limit(limit)
        )
        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def count(self) -> int:
        statement = select(func.count()).select_from(Spacecraft)
        result = await self._session.execute(statement)

        return result.scalar_one()

    async def delete(self, spacecraft: Spacecraft) -> None:
        await self._session.delete(spacecraft)
