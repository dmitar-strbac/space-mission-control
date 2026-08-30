from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums import SagaStepStatus, SagaStepType


class SagaStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    saga_id: UUID
    mission_id: UUID

    step_type: SagaStepType
    status: SagaStepStatus

    failure_reason: str | None

    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None
    compensated_at: datetime | None


class MissionPreparationResponse(BaseModel):
    mission_id: UUID
    saga_id: UUID | None
    steps: list[SagaStepResponse]
