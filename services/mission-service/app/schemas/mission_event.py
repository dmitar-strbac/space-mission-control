from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums import MissionEventType


class MissionEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mission_id: UUID
    event_type: MissionEventType
    source: str
    payload: dict[str, Any]
    occurred_at: datetime
