from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.domain.faults import FaultType
from app.messaging.fault_publisher import (
    publish_fault_cleared,
)
from app.messaging.publisher import event_bus
from app.schemas.fault import (
    FaultInjectionRequest,
    FaultInjectionResponse,
)
from app.services.fault_service import (
    FaultInjectionError,
    FaultService,
)

settings = get_settings()

router = APIRouter(
    prefix="/faults",
    tags=["faults"],
)

fault_service = FaultService()


@router.post(
    "/inject",
    response_model=FaultInjectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def inject_fault(
    request: FaultInjectionRequest,
) -> FaultInjectionResponse:
    try:
        fault = fault_service.inject(
            mission_id=request.mission_id,
            fault_type=request.fault_type,
            magnitude=request.magnitude,
        )
    except FaultInjectionError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return FaultInjectionResponse(
        mission_id=request.mission_id,
        fault_type=fault.fault_type,
        magnitude=fault.magnitude,
        active=True,
    )


@router.delete(
    "/{mission_id}/{fault_type}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_fault(
    mission_id: UUID,
    fault_type: FaultType,
) -> None:
    try:
        fault_service.clear(
            mission_id=mission_id,
            fault_type=fault_type,
        )

        if settings.messaging_enabled:
            await publish_fault_cleared(
                event_bus=event_bus,
                mission_id=mission_id,
                fault_type=fault_type,
            )
    except FaultInjectionError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
