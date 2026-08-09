from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.enums import LaunchWindowStatus


class LaunchWindowCalculateRequest(BaseModel):
    mission_id: UUID
    requested_time: datetime
    window_score: int = Field(ge=0, le=100)
    feasible: bool

    @model_validator(mode="after")
    def validate_requested_time(self) -> Self:
        if self.requested_time.tzinfo is None:
            raise ValueError("requested_time must include timezone information")

        return self


class LaunchWindowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mission_id: UUID

    window_start: datetime
    window_end: datetime
    preferred_time: datetime

    window_score: int
    status: LaunchWindowStatus
    reason: str | None

    created_at: datetime
