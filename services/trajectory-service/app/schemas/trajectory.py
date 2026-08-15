from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.enums import (
    ManeuverStatus,
    ManeuverType,
    ReferenceFrame,
    TrajectoryStatus,
)


class Vector2DSchema(BaseModel):
    x: float
    y: float


class StateVectorSchema(BaseModel):
    position: Vector2DSchema
    velocity: Vector2DSchema
    total_mass_kg: float = Field(gt=0)
    propellant_mass_kg: float = Field(ge=0)
    elapsed_time_s: float = Field(default=0, ge=0)


class TrajectoryPlanRequest(BaseModel):
    mission_id: UUID

    initial_altitude_m: float = Field(ge=0)
    target_altitude_m: float = Field(ge=0)

    total_mass_kg: float = Field(gt=0)
    available_propellant_kg: float = Field(ge=0)
    engine_specific_impulse_s: float = Field(gt=0)

    departure_time: datetime

    minimum_propellant_reserve_percent: float = Field(
        default=10.0,
        ge=0,
        lt=100,
    )

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.departure_time.tzinfo is None:
            raise ValueError("departure_time must include timezone information")

        if self.available_propellant_kg > self.total_mass_kg:
            raise ValueError("available_propellant_kg cannot exceed total_mass_kg")

        return self


class ManeuverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sequence: int
    maneuver_type: ManeuverType
    delta_v_m_s: float
    planned_offset_s: float
    status: ManeuverStatus


class TrajectoryPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mission_id: UUID
    reference_frame: ReferenceFrame

    departure_time: datetime
    arrival_time: datetime

    initial_state_vector: dict[str, object]
    target_state_vector: dict[str, object]

    required_delta_v_m_s: float
    estimated_propellant_kg: float
    propellant_reserve_percent: float
    safety_margin_percent: float
    window_score: int

    status: TrajectoryStatus
    created_at: datetime

    maneuvers: list[ManeuverResponse]


class SafeReturnPlanRequest(BaseModel):
    mission_id: UUID

    current_state_vector: StateVectorSchema

    engine_specific_impulse_s: float = Field(gt=0)

    departure_time: datetime

    entry_interface_altitude_m: float = Field(
        default=120_000.0,
        gt=0,
    )

    @model_validator(mode="after")
    def validate_departure_time(self) -> Self:
        if self.departure_time.tzinfo is None:
            raise ValueError("departure_time must include timezone information")

        return self
