from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.core.database import get_database
from app.repositories.alert_repository import AlertRepository
from app.repositories.anomaly_repository import AnomalyRepository
from app.schemas.alerts import (
    AlertRecord,
    AnomalyEvent,
)

router = APIRouter(
    prefix="/missions/{mission_id}",
    tags=["Safety"],
)


def get_alert_repository() -> AlertRepository:
    return AlertRepository(get_database())


def get_anomaly_repository() -> AnomalyRepository:
    return AnomalyRepository(get_database())


AlertRepositoryDependency = Annotated[
    AlertRepository,
    Depends(get_alert_repository),
]

AnomalyRepositoryDependency = Annotated[
    AnomalyRepository,
    Depends(get_anomaly_repository),
]


@router.get(
    "/alerts",
    response_model=list[AlertRecord],
)
async def get_mission_alerts(
    mission_id: UUID,
    repository: AlertRepositoryDependency,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
) -> list[AlertRecord]:
    return await repository.list_by_mission(
        mission_id,
        limit=limit,
    )


@router.get(
    "/anomalies",
    response_model=list[AnomalyEvent],
)
async def get_mission_anomalies(
    mission_id: UUID,
    repository: AnomalyRepositoryDependency,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
) -> list[AnomalyEvent]:
    return await repository.list_by_mission(
        mission_id,
        limit=limit,
    )
