from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.enums import MissionPhase, MissionStatus, MissionType


class MissionCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    mission_type: MissionType
    vehicle_id: UUID | None = None
    crew_count: int = Field(default=0, ge=0)
    target_type: str = Field(min_length=1, max_length=50)
    target_parameters: dict[str, Any]
    planned_launch_time: datetime | None = None
    simulation_speed: int = Field(default=1)

    @model_validator(mode="after")
    def validate_business_fields(self) -> Self:
        if self.simulation_speed not in {1, 10, 60, 300}:
            raise ValueError("simulation_speed must be one of: 1, 10, 60, 300")
        if self.planned_launch_time is not None and self.planned_launch_time.tzinfo is None:
            raise ValueError("planned_launch_time must include timezone information")
        return self


class MissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    mission_type: MissionType
    status: MissionStatus
    mission_phase: MissionPhase | None
    vehicle_id: UUID | None
    crew_count: int
    target_type: str
    target_parameters: dict[str, Any]
    planned_launch_time: datetime | None
    simulation_speed: int
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    failure_reason: str | None


class MissionListResponse(BaseModel):
    items: list[MissionResponse]
    total: int
    limit: int
    offset: int
