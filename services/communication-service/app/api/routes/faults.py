from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.messaging.fault_publisher import (
    publish_communication_fault_cleared,
    publish_communication_fault_injected,
)
from app.messaging.publisher import event_bus
from app.messaging.status_publisher import publish_communication_status
from app.schemas.fault import (
    CommunicationFaultResponse,
    CommunicationLossInjectionRequest,
)
from app.services.communication_service import CommunicationService

settings = get_settings()

router = APIRouter(
    prefix="/faults",
    tags=["Faults"],
)

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@router.post(
    "/communication-loss",
    response_model=CommunicationFaultResponse,
    status_code=status.HTTP_200_OK,
)
async def inject_communication_loss(
    payload: CommunicationLossInjectionRequest,
    session: SessionDependency,
) -> CommunicationFaultResponse:
    profile = await CommunicationService(session).inject_communication_loss(payload.mission_id)

    if settings.messaging_enabled:
        await publish_communication_fault_injected(
            event_bus=event_bus,
            mission_id=payload.mission_id,
        )

        await publish_communication_status(
            event_bus=event_bus,
            profile=profile,
        )

    return CommunicationFaultResponse(
        mission_id=payload.mission_id,
        signal_status=profile.signal_status.value,
    )


@router.delete(
    "/communication-loss/{mission_id}",
    response_model=CommunicationFaultResponse,
)
async def clear_communication_loss(
    mission_id: UUID,
    session: SessionDependency,
) -> CommunicationFaultResponse:
    profile = await CommunicationService(session).restore_communication(mission_id)

    if settings.messaging_enabled:
        await publish_communication_fault_cleared(
            event_bus=event_bus,
            mission_id=mission_id,
        )

        await publish_communication_status(
            event_bus=event_bus,
            profile=profile,
        )

    return CommunicationFaultResponse(
        mission_id=mission_id,
        signal_status=profile.signal_status.value,
    )
