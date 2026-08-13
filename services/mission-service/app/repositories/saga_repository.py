from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import (
    SagaStepStatus,
    SagaStepType,
)
from app.models.saga_step import SagaStep


class SagaRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    def add(
        self,
        step: SagaStep,
    ) -> None:
        self._session.add(step)

    def add_all(
        self,
        steps: list[SagaStep],
    ) -> None:
        self._session.add_all(steps)

    async def get_step(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
        for_update: bool = False,
    ) -> SagaStep | None:
        statement = select(SagaStep).where(
            SagaStep.saga_id == saga_id,
            SagaStep.step_type == step_type,
        )

        if for_update:
            statement = statement.with_for_update()

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_steps(
        self,
        saga_id: UUID,
    ) -> Sequence[SagaStep]:
        statement = (
            select(SagaStep).where(SagaStep.saga_id == saga_id).order_by(SagaStep.created_at.asc())
        )

        result = await self._session.scalars(statement)

        return result.all()

    async def get_active_step(
        self,
        saga_id: UUID,
        *,
        for_update: bool = False,
    ) -> SagaStep | None:
        statement = select(SagaStep).where(
            SagaStep.saga_id == saga_id,
            SagaStep.status == SagaStepStatus.IN_PROGRESS,
        )

        if for_update:
            statement = statement.with_for_update()

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_latest_saga_id_for_mission(
        self,
        mission_id: UUID,
    ) -> UUID | None:
        statement = (
            select(SagaStep.saga_id)
            .where(SagaStep.mission_id == mission_id)
            .order_by(SagaStep.created_at.desc())
            .limit(1)
        )

        result = await self._session.scalar(statement)

        return result
