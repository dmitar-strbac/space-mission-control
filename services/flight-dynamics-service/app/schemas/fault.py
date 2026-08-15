from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.faults import FaultType


class FaultInjectionRequest(BaseModel):
    mission_id: UUID

    fault_type: FaultType

    magnitude: float = Field(
        ge=0.0,
    )


class FaultInjectionResponse(BaseModel):
    mission_id: UUID

    fault_type: FaultType

    magnitude: float

    active: bool
