from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import MissionType, ValidationViolationCode


class SpacecraftValidationRequest(BaseModel):
    mission_type: MissionType
    crew_count: int = Field(ge=0)
    payload_mass_kg: float = Field(ge=0)
    estimated_duration_h: float = Field(gt=0)


class ValidationViolation(BaseModel):
    code: ValidationViolationCode
    message: str


class SpacecraftValidationResponse(BaseModel):
    spacecraft_id: UUID
    valid: bool
    initial_mass_kg: float
    available_delta_v_m_s: float
    violations: list[ValidationViolation]
