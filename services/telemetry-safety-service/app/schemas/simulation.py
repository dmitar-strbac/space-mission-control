from uuid import UUID

from pydantic import BaseModel, Field


class Vector2DInput(BaseModel):
    x: float
    y: float


class SimulationStateEventPayload(BaseModel):
    mission_id: UUID
    simulation_session_id: UUID

    simulation_time_s: float = Field(ge=0)

    position: Vector2DInput
    velocity: Vector2DInput

    total_mass_kg: float = Field(gt=0)

    propellant_kg: float = Field(ge=0)
    initial_propellant_kg: float = Field(ge=0)

    oxygen_kg: float = Field(ge=0)
    initial_oxygen_kg: float = Field(ge=0)
    oxygen_consumption_rate_kg_s: float = Field(ge=0)

    battery_kwh: float = Field(ge=0)
    initial_battery_kwh: float = Field(ge=0)
    power_consumption_kw: float = Field(ge=0)

    engine_thrust_n: float = Field(ge=0)
    engine_specific_impulse_s: float = Field(gt=0)

    active_maneuver_id: UUID | None = None
