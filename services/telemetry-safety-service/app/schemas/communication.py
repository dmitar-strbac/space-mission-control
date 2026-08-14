from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommunicationStatusEventPayload(BaseModel):
    mission_id: UUID

    signal_status: str

    one_way_delay_ms: float = Field(ge=0)
    packet_loss_percent: float = Field(
        ge=0,
        le=100,
    )

    observed_at: datetime
