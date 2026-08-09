from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.trajectory import (
    ManeuverResponse,
    TrajectoryPlanRequest,
    TrajectoryPlanResponse,
)
from app.services.trajectory_service import TrajectoryService

router = APIRouter(
    prefix="/trajectories",
    tags=["Trajectories"],
)

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@router.post(
    "/plan",
    response_model=TrajectoryPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def plan_trajectory(
    payload: TrajectoryPlanRequest,
    session: SessionDependency,
) -> TrajectoryPlanResponse:
    trajectory_plan = await TrajectoryService(session).plan(payload)

    return TrajectoryPlanResponse.model_validate(trajectory_plan)


@router.get(
    "/{mission_id}",
    response_model=TrajectoryPlanResponse,
)
async def get_trajectory_plan(
    mission_id: UUID,
    session: SessionDependency,
) -> TrajectoryPlanResponse:
    trajectory_plan = await TrajectoryService(session).get(mission_id)

    return TrajectoryPlanResponse.model_validate(trajectory_plan)


@router.get(
    "/{mission_id}/maneuvers",
    response_model=list[ManeuverResponse],
)
async def get_maneuvers(
    mission_id: UUID,
    session: SessionDependency,
) -> list[ManeuverResponse]:
    maneuvers = await TrajectoryService(session).get_maneuvers(mission_id)

    return [ManeuverResponse.model_validate(maneuver) for maneuver in maneuvers]
