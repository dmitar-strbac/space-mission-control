from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.messaging.publisher import (
    EventPublisher,
    get_event_publisher,
)
from app.schemas.mission import MissionCreate, MissionListResponse, MissionResponse
from app.schemas.mission_event import MissionEventResponse
from app.schemas.preparation import (
    MissionPreparationResponse,
    SagaStepResponse,
)
from app.services.abort_workflow import AbortWorkflowService
from app.services.launch_workflow import LaunchWorkflowService
from app.services.mission_service import MissionService
from app.services.prepare_mission_saga import PrepareMissionSagaService
from app.services.saga_step_service import SagaStepService

router = APIRouter(prefix="/missions", tags=["Missions"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]
PublisherDependency = Annotated[
    EventPublisher,
    Depends(get_event_publisher),
]


@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(payload: MissionCreate, session: SessionDependency) -> MissionResponse:
    mission = await MissionService(session).create(payload)
    return MissionResponse.model_validate(mission)


@router.get("", response_model=MissionListResponse)
async def list_missions(
    session: SessionDependency,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> MissionListResponse:
    missions, total = await MissionService(session).list(limit=limit, offset=offset)
    return MissionListResponse(
        items=[MissionResponse.model_validate(item) for item in missions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: UUID, session: SessionDependency) -> MissionResponse:
    mission = await MissionService(session).get(mission_id)
    return MissionResponse.model_validate(mission)


@router.post(
    "/{mission_id}/prepare",
    response_model=MissionResponse,
)
async def prepare_mission(
    mission_id: UUID,
    session: SessionDependency,
    publisher: PublisherDependency,
) -> MissionResponse:
    mission = await PrepareMissionSagaService(
        session,
        publisher,
    ).start(mission_id)

    return MissionResponse.model_validate(mission)


@router.post(
    "/{mission_id}/launch",
    response_model=MissionResponse,
)
async def launch_mission(
    mission_id: UUID,
    session: SessionDependency,
    publisher: PublisherDependency,
) -> MissionResponse:
    mission = await LaunchWorkflowService(
        MissionService(session),
        publisher,
    ).launch(mission_id)

    return MissionResponse.model_validate(mission)


@router.post(
    "/{mission_id}/abort",
    response_model=MissionResponse,
)
async def abort_mission(
    mission_id: UUID,
    session: SessionDependency,
    publisher: PublisherDependency,
) -> MissionResponse:
    mission = await AbortWorkflowService(
        MissionService(session),
        publisher,
    ).request_abort(
        mission_id,
        reason="Emergency Abort requested by operator.",
    )

    return MissionResponse.model_validate(mission)


@router.get(
    "/{mission_id}/preparation",
    response_model=MissionPreparationResponse,
)
async def get_mission_preparation(
    mission_id: UUID,
    session: SessionDependency,
) -> MissionPreparationResponse:
    await MissionService(session).get(mission_id)

    saga_id, steps = await SagaStepService(
        session,
    ).get_latest_steps_for_mission(mission_id)

    return MissionPreparationResponse(
        mission_id=mission_id,
        saga_id=saga_id,
        steps=[SagaStepResponse.model_validate(step) for step in steps],
    )


@router.get("/{mission_id}/timeline", response_model=list[MissionEventResponse])
async def get_mission_timeline(
    mission_id: UUID, session: SessionDependency
) -> list[MissionEventResponse]:
    events = await MissionService(session).timeline(mission_id)
    return [MissionEventResponse.model_validate(event) for event in events]
