from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.messaging.publisher import event_bus
from app.messaging.status_publisher import publish_communication_status
from app.schemas.communication_profile import (
    CommunicationProfileCreateRequest,
    CommunicationProfileResponse,
    CommunicationProfileUpdateRequest,
)
from app.services.communication_service import CommunicationService

settings = get_settings()

router = APIRouter(
    prefix="/communication-profiles",
    tags=["Communication Profiles"],
)

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@router.post(
    "",
    response_model=CommunicationProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_communication_profile(
    payload: CommunicationProfileCreateRequest,
    session: SessionDependency,
) -> CommunicationProfileResponse:
    profile = await CommunicationService(session).create_profile(payload)

    if settings.messaging_enabled:
        await publish_communication_status(
            event_bus=event_bus,
            profile=profile,
        )

    return CommunicationProfileResponse.model_validate(profile)


@router.get(
    "/{mission_id}",
    response_model=CommunicationProfileResponse,
)
async def get_communication_profile(
    mission_id: UUID,
    session: SessionDependency,
) -> CommunicationProfileResponse:
    profile = await CommunicationService(session).get_profile(mission_id)

    return CommunicationProfileResponse.model_validate(profile)


@router.patch(
    "/{mission_id}",
    response_model=CommunicationProfileResponse,
)
async def update_communication_profile(
    mission_id: UUID,
    payload: CommunicationProfileUpdateRequest,
    session: SessionDependency,
) -> CommunicationProfileResponse:
    profile = await CommunicationService(session).update_profile(
        mission_id,
        payload,
    )

    if settings.messaging_enabled:
        await publish_communication_status(
            event_bus=event_bus,
            profile=profile,
        )

    return CommunicationProfileResponse.model_validate(profile)
