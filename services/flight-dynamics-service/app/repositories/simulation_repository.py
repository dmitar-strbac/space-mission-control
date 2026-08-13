from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulation_checkpoint import (
    SimulationCheckpoint,
)
from app.models.simulation_session import (
    SimulationSession,
)


class SimulationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    def add_session(
        self,
        simulation: SimulationSession,
    ) -> None:
        self._session.add(simulation)

    def add_checkpoint(
        self,
        checkpoint: SimulationCheckpoint,
    ) -> None:
        self._session.add(checkpoint)

    async def get_by_mission_id(
        self,
        mission_id: UUID,
        *,
        for_update: bool = False,
    ) -> SimulationSession | None:
        statement = select(SimulationSession).where(SimulationSession.mission_id == mission_id)

        if for_update:
            statement = statement.with_for_update()

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_checkpoints(
        self,
        simulation_session_id: UUID,
    ) -> Sequence[SimulationCheckpoint]:
        result = await self._session.scalars(
            select(SimulationCheckpoint)
            .where(SimulationCheckpoint.simulation_session_id == simulation_session_id)
            .order_by(
                SimulationCheckpoint.simulated_time_s.asc(),
                SimulationCheckpoint.created_at.asc(),
            )
        )

        return result.all()

    async def delete_session(
        self,
        simulation: SimulationSession,
    ) -> None:
        await self._session.delete(simulation)
