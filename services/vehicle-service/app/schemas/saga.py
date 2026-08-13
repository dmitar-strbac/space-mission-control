from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import MissionType


class VehicleReservationRequest(BaseModel):
    saga_id: UUID
    mission_id: UUID
    vehicle_id: UUID

    mission_type: MissionType
    crew_count: int = Field(ge=0)
    payload_mass_kg: float = Field(
        default=0.0,
        ge=0,
    )


class FinalResourceValidationRequest(BaseModel):
    saga_id: UUID
    mission_id: UUID
    vehicle_id: UUID

    total_mass_kg: float = Field(gt=0)
    required_propellant_kg: float = Field(ge=0)

    minimum_propellant_reserve_percent: float = Field(
        default=10.0,
        ge=0,
        lt=100,
    )

    mission_duration_s: float = Field(
        ge=0,
    )

    oxygen_consumption_rate_kg_s: float = Field(
        default=0.0,
        ge=0,
    )

    power_consumption_kw: float = Field(
        default=0.0,
        ge=0,
    )
