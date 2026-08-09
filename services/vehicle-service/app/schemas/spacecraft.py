from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.enums import MissionType, SpacecraftStatus, VehicleType


class SpacecraftConfigurationBase(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=120,
    )
    vehicle_type: VehicleType
    supported_mission_types: list[MissionType] = Field(
        min_length=1,
    )

    dry_mass_kg: float = Field(gt=0)
    max_payload_kg: float = Field(ge=0)
    crew_capacity: int = Field(ge=0)

    engine_thrust_n: float = Field(gt=0)
    engine_specific_impulse_s: float = Field(gt=0)
    propellant_capacity_kg: float = Field(gt=0)

    oxygen_capacity_kg: float = Field(ge=0)
    battery_capacity_kwh: float = Field(gt=0)

    max_mission_duration_h: float = Field(gt=0)
    max_acceleration_g: float = Field(gt=0)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())

        if not normalized:
            raise ValueError("Spacecraft name must not be blank.")

        return normalized

    @field_validator("supported_mission_types")
    @classmethod
    def ensure_unique_mission_types(
        cls,
        value: list[MissionType],
    ) -> list[MissionType]:
        if len(value) != len(set(value)):
            raise ValueError("Supported mission types must be unique.")

        return value

    @model_validator(mode="after")
    def validate_vehicle_configuration(self) -> "SpacecraftConfigurationBase":
        if self.crew_capacity > 0 and self.oxygen_capacity_kg <= 0:
            raise ValueError("Crewed spacecraft must provide a positive oxygen capacity.")

        return self


class SpacecraftCreate(SpacecraftConfigurationBase):
    pass


class SpacecraftUpdate(SpacecraftConfigurationBase):
    status: SpacecraftStatus = SpacecraftStatus.AVAILABLE


class SpacecraftResponse(SpacecraftConfigurationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: SpacecraftStatus
    fully_fueled_mass_kg: float
    created_at: datetime
    updated_at: datetime


class SpacecraftListResponse(BaseModel):
    items: list[SpacecraftResponse]
    total: int
    offset: int
    limit: int
