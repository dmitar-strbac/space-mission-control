from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.maneuver import Maneuver
from app.models.trajectory_plan import TrajectoryPlan


class TrajectoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, trajectory_plan: TrajectoryPlan) -> None:
        self._session.add(trajectory_plan)

    async def get_by_mission_id(
        self,
        mission_id: UUID,
    ) -> TrajectoryPlan | None:
        statement = (
            select(TrajectoryPlan)
            .options(selectinload(TrajectoryPlan.maneuvers))
            .where(TrajectoryPlan.mission_id == mission_id)
            .order_by(TrajectoryPlan.created_at.desc())
            .limit(1)
        )

        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def get_maneuvers(
        self,
        mission_id: UUID,
    ) -> Sequence[Maneuver]:
        trajectory_plan = await self.get_by_mission_id(mission_id)

        if trajectory_plan is None:
            return ()

        return trajectory_plan.maneuvers
