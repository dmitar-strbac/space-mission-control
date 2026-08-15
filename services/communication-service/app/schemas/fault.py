from uuid import UUID

from pydantic import BaseModel


class CommunicationLossInjectionRequest(BaseModel):
    mission_id: UUID


class CommunicationFaultResponse(BaseModel):
    mission_id: UUID
    signal_status: str
