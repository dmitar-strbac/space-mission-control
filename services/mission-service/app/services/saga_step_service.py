from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import (
    SagaStepStatus,
    SagaStepType,
)
from app.domain.saga import (
    PREPARE_MISSION_STEP_ORDER,
)
from app.models.saga_step import SagaStep
from app.repositories.saga_repository import (
    SagaRepository,
)


class SagaStepService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._repository = SagaRepository(session)

    async def create_prepare_steps(
        self,
        *,
        saga_id: UUID,
        mission_id: UUID,
    ) -> list[SagaStep]:
        steps = [
            SagaStep(
                saga_id=saga_id,
                mission_id=mission_id,
                step_type=step_type,
                status=SagaStepStatus.PENDING,
            )
            for step_type in PREPARE_MISSION_STEP_ORDER
        ]

        self._repository.add_all(steps)

        await self._session.flush()

        return steps

    async def mark_in_progress(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
        request_event_id: UUID,
        request_payload: dict[str, Any],
    ) -> SagaStep:
        step = await self._require_step(
            saga_id=saga_id,
            step_type=step_type,
        )

        step.status = SagaStepStatus.IN_PROGRESS
        step.request_event_id = request_event_id
        step.request_payload = request_payload
        step.started_at = datetime.now(UTC)

        step.result_event_id = None
        step.result_payload = None
        step.failure_reason = None
        step.completed_at = None
        step.failed_at = None

        await self._session.flush()

        return step

    async def mark_completed(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
        result_event_id: UUID,
        result_payload: dict[str, Any],
    ) -> SagaStep:
        step = await self._require_step(
            saga_id=saga_id,
            step_type=step_type,
        )

        step.status = SagaStepStatus.COMPLETED
        step.result_event_id = result_event_id
        step.result_payload = result_payload
        step.completed_at = datetime.now(UTC)

        await self._session.flush()

        return step

    async def mark_failed(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
        result_event_id: UUID,
        result_payload: dict[str, Any],
        reason: str,
    ) -> SagaStep:
        step = await self._require_step(
            saga_id=saga_id,
            step_type=step_type,
        )

        step.status = SagaStepStatus.FAILED
        step.result_event_id = result_event_id
        step.result_payload = result_payload
        step.failure_reason = reason
        step.failed_at = datetime.now(UTC)

        await self._session.flush()

        return step

    async def mark_compensating(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
    ) -> SagaStep:
        step = await self._require_step(
            saga_id=saga_id,
            step_type=step_type,
        )

        step.status = SagaStepStatus.COMPENSATING

        await self._session.flush()

        return step

    async def mark_compensated(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
    ) -> SagaStep:
        step = await self._require_step(
            saga_id=saga_id,
            step_type=step_type,
        )

        step.status = SagaStepStatus.COMPENSATED
        step.compensated_at = datetime.now(UTC)

        await self._session.flush()

        return step

    async def get_result_payload(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
    ) -> dict[str, Any] | None:
        step = await self._repository.get_step(
            saga_id=saga_id,
            step_type=step_type,
        )

        if step is None:
            return None

        return step.result_payload

    async def _require_step(
        self,
        *,
        saga_id: UUID,
        step_type: SagaStepType,
    ) -> SagaStep:
        step = await self._repository.get_step(
            saga_id=saga_id,
            step_type=step_type,
            for_update=True,
        )

        if step is None:
            raise RuntimeError(f"Saga step was not initialized: {saga_id} / {step_type.value}")

        return step
