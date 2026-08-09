from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.enums import (
    CheckpointReason,
    ManeuverExecutionStatus,
    ManeuverType,
    SimulationStatus,
)
from app.domain.simulation import validate_simulation_speed


class Vector2DSchema(BaseModel):
    x: float
    y: float


class StateVectorSchema(BaseModel):
    position: Vector2DSchema
    velocity: Vector2DSchema
    total_mass_kg: float = Field(gt=0)
    propellant_mass_kg: float = Field(ge=0)
    elapsed_time_s: float = Field(default=0.0, ge=0)

    @model_validator(mode="after")
    def validate_mass(self) -> Self:
        if self.propellant_mass_kg > self.total_mass_kg:
            raise ValueError("propellant_mass_kg cannot exceed total_mass_kg")

        return self


class PlannedManeuverSchema(BaseModel):
    id: UUID
    sequence: int = Field(ge=1)
    maneuver_type: ManeuverType
    delta_v_m_s: float = Field(gt=0)
    planned_offset_s: float = Field(ge=0)
    direction: Vector2DSchema | None = None


class SimulationInitializeRequest(BaseModel):
    mission_id: UUID
    trajectory_plan_id: UUID
    vehicle_id: UUID

    initial_state_vector: StateVectorSchema
    planned_maneuvers: list[PlannedManeuverSchema] = Field(default_factory=list)

    engine_thrust_n: float = Field(gt=0)
    engine_specific_impulse_s: float = Field(gt=0)

    oxygen_kg: float = Field(default=0.0, ge=0)
    oxygen_consumption_rate_kg_s: float = Field(
        default=0.0,
        ge=0,
    )

    battery_kwh: float = Field(default=0.0, ge=0)
    power_consumption_kw: float = Field(
        default=0.0,
        ge=0,
    )

    simulation_speed: int = 1

    integration_step_s: float = Field(
        default=1.0,
        gt=0,
        le=10.0,
    )

    checkpoint_interval_s: float = Field(
        default=60.0,
        gt=0,
    )

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        validate_simulation_speed(self.simulation_speed)
        return self


class SimulationAdvanceRequest(BaseModel):
    real_duration_s: float = Field(
        gt=0,
        le=60,
    )


class ManeuverExecutionResponse(BaseModel):
    id: UUID
    sequence: int
    maneuver_type: ManeuverType
    status: ManeuverExecutionStatus
    delta_v_m_s: float
    planned_offset_s: float
    remaining_burn_s: float | None


class SimulationStateResponse(BaseModel):
    position: Vector2DSchema
    velocity: Vector2DSchema

    total_mass_kg: float
    propellant_mass_kg: float
    elapsed_time_s: float

    oxygen_kg: float
    battery_kwh: float

    maneuvers: list[ManeuverExecutionResponse]


class SimulationAdvanceResponse(BaseModel):
    simulated_duration_s: float
    state: SimulationStateResponse


class SimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mission_id: UUID
    trajectory_plan_id: UUID
    vehicle_id: UUID

    status: SimulationStatus

    simulation_speed: int
    integration_step_s: float
    checkpoint_interval_s: float

    initial_state_vector: dict[str, object]
    planned_maneuvers: list[dict[str, object]]

    engine_thrust_n: float
    engine_specific_impulse_s: float

    oxygen_kg: float
    oxygen_consumption_rate_kg_s: float

    battery_kwh: float
    power_consumption_kw: float

    created_at: datetime
    started_at: datetime | None
    paused_at: datetime | None
    completed_at: datetime | None
    failure_reason: str | None


class SimulationCheckpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    simulation_session_id: UUID
    simulated_time_s: float

    state_vector: dict[str, object]

    oxygen_kg: float
    battery_kwh: float

    maneuver_states: list[dict[str, object]]

    reason: CheckpointReason
    created_at: datetime
