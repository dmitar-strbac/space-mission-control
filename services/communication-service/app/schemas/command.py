from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import (
    CommandStatus,
    CommandType,
)


class CommandCreateRequest(BaseModel):
    mission_id: UUID
    command_type: CommandType
    payload: dict[str, Any] = Field(default_factory=dict)


class CommandRejectRequest(BaseModel):
    reason: str = Field(
        min_length=1,
        max_length=500,
    )


class CommandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mission_id: UUID

    command_type: CommandType
    payload: dict[str, Any]

    issued_at: datetime
    scheduled_delivery_at: datetime | None
    received_at: datetime | None
    executed_at: datetime | None

    status: CommandStatus
    rejection_reason: str | None


class CommandLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    command_id: UUID

    previous_status: CommandStatus | None
    new_status: CommandStatus

    message: str | None
    occurred_at: datetime


class CommandDispatchResponse(BaseModel):
    command: CommandResponse
    one_way_delay_ms: float
