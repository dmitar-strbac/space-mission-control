from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.spacecraft import (
    SpacecraftCreate,
    SpacecraftListResponse,
    SpacecraftResponse,
    SpacecraftUpdate,
)
from app.schemas.validation import (
    SpacecraftValidationRequest,
    SpacecraftValidationResponse,
)
from app.services.spacecraft_service import SpacecraftService

router = APIRouter(
    prefix="/spacecraft",
    tags=["Spacecraft"],
)

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@router.post(
    "",
    response_model=SpacecraftResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_spacecraft(
    request: SpacecraftCreate,
    session: SessionDependency,
) -> SpacecraftResponse:
    spacecraft = await SpacecraftService(session).create(request)

    return SpacecraftResponse.model_validate(spacecraft)


@router.get(
    "",
    response_model=SpacecraftListResponse,
)
async def list_spacecraft(
    session: SessionDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SpacecraftListResponse:
    return await SpacecraftService(session).list(
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{spacecraft_id}",
    response_model=SpacecraftResponse,
)
async def get_spacecraft(
    spacecraft_id: UUID,
    session: SessionDependency,
) -> SpacecraftResponse:
    spacecraft = await SpacecraftService(session).get(spacecraft_id)

    return SpacecraftResponse.model_validate(spacecraft)


@router.put(
    "/{spacecraft_id}",
    response_model=SpacecraftResponse,
)
async def update_spacecraft(
    spacecraft_id: UUID,
    request: SpacecraftUpdate,
    session: SessionDependency,
) -> SpacecraftResponse:
    spacecraft = await SpacecraftService(session).update(
        spacecraft_id,
        request,
    )

    return SpacecraftResponse.model_validate(spacecraft)


@router.delete(
    "/{spacecraft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_spacecraft(
    spacecraft_id: UUID,
    session: SessionDependency,
) -> Response:
    await SpacecraftService(session).delete(spacecraft_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{spacecraft_id}/validate",
    response_model=SpacecraftValidationResponse,
)
async def validate_spacecraft(
    spacecraft_id: UUID,
    request: SpacecraftValidationRequest,
    session: SessionDependency,
) -> SpacecraftValidationResponse:
    return await SpacecraftService(session).validate(
        spacecraft_id,
        request,
    )
