from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import SignalStatus


class CommunicationProfileCreateRequest(BaseModel):
    mission_id: UUID

    distance_m: float = Field(
        ge=0,
    )

    additional_latency_ms: float = Field(
        default=0.0,
        ge=0,
    )

    packet_loss_percent: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    signal_status: SignalStatus = SignalStatus.AVAILABLE


class CommunicationProfileUpdateRequest(BaseModel):
    distance_m: float | None = Field(
        default=None,
        ge=0,
    )

    additional_latency_ms: float | None = Field(
        default=None,
        ge=0,
    )

    packet_loss_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    signal_status: SignalStatus | None = None


class CommunicationProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mission_id: UUID

    distance_m: float
    additional_latency_ms: float
    packet_loss_percent: float
    signal_status: SignalStatus

    created_at: datetime
    updated_at: datetime
