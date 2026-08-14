from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.core.database import get_database
from app.repositories.telemetry_repository import TelemetryRepository
from app.schemas.telemetry import TelemetryPoint

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
)


def get_telemetry_repository() -> TelemetryRepository:
    return TelemetryRepository(get_database())


RepositoryDependency = Annotated[
    TelemetryRepository,
    Depends(get_telemetry_repository),
]


@router.get(
    "/{mission_id}",
    response_model=list[TelemetryPoint],
)
async def get_recent_telemetry(
    mission_id: UUID,
    repository: RepositoryDependency,
    limit: int = Query(
        default=300,
        ge=1,
        le=300,
    ),
) -> list[TelemetryPoint]:
    return await repository.list_recent(
        mission_id,
        limit=limit,
    )


@router.get(
    "/{mission_id}/latest",
    response_model=TelemetryPoint | None,
)
async def get_latest_telemetry(
    mission_id: UUID,
    repository: RepositoryDependency,
) -> TelemetryPoint | None:
    return await repository.get_latest(mission_id)
