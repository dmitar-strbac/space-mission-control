from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resource_reservation import (
    ResourceReservation,
)


class ResourceReservationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    def add(
        self,
        reservation: ResourceReservation,
    ) -> None:
        self._session.add(reservation)

    async def get_by_mission_id(
        self,
        mission_id: UUID,
    ) -> ResourceReservation | None:
        statement = select(ResourceReservation).where(ResourceReservation.mission_id == mission_id)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_spacecraft_id(
        self,
        spacecraft_id: UUID,
    ) -> ResourceReservation | None:
        statement = select(ResourceReservation).where(
            ResourceReservation.spacecraft_id == spacecraft_id
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def delete(
        self,
        reservation: ResourceReservation,
    ) -> None:
        await self._session.delete(reservation)
