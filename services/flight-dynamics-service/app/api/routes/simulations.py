from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.serialization import simulation_state_response
from app.core.config import get_settings
from app.core.database import get_session
from app.messaging.publisher import event_bus
from app.messaging.state_publisher import publish_simulation_state
from app.schemas.simulation import (
    SimulationAdvanceRequest,
    SimulationAdvanceResponse,
    SimulationCheckpointResponse,
    SimulationInitializeRequest,
    SimulationResponse,
    SimulationStateResponse,
)
from app.services.simulation_runtime import simulation_runtime_manager
from app.services.simulation_service import SimulationService

router = APIRouter(
    prefix="/simulations",
    tags=["Simulations"],
)

settings = get_settings()

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@router.post(
    "/initialize",
    response_model=SimulationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def initialize_simulation(
    payload: SimulationInitializeRequest,
    session: SessionDependency,
) -> SimulationResponse:
    simulation = await SimulationService(session).initialize(payload)

    return SimulationResponse.model_validate(simulation)


@router.get(
    "/{mission_id}",
    response_model=SimulationResponse,
)
async def get_simulation(
    mission_id: UUID,
    session: SessionDependency,
) -> SimulationResponse:
    simulation = await SimulationService(session).get(mission_id)

    return SimulationResponse.model_validate(simulation)


@router.post(
    "/{mission_id}/start",
    response_model=SimulationResponse,
)
async def start_simulation(
    mission_id: UUID,
    session: SessionDependency,
) -> SimulationResponse:
    simulation = await SimulationService(session).start(mission_id)

    simulation_runtime_manager.start(
        mission_id,
    )

    return SimulationResponse.model_validate(simulation)


@router.post(
    "/{mission_id}/pause",
    response_model=SimulationResponse,
)
async def pause_simulation(
    mission_id: UUID,
    session: SessionDependency,
) -> SimulationResponse:
    simulation = await SimulationService(session).pause(mission_id)

    await simulation_runtime_manager.stop(
        mission_id,
    )

    return SimulationResponse.model_validate(simulation)


@router.post(
    "/{mission_id}/resume",
    response_model=SimulationResponse,
)
async def resume_simulation(
    mission_id: UUID,
    session: SessionDependency,
) -> SimulationResponse:
    simulation = await SimulationService(session).resume(mission_id)

    simulation_runtime_manager.start(
        mission_id,
    )

    return SimulationResponse.model_validate(simulation)


@router.post(
    "/{mission_id}/advance",
    response_model=SimulationAdvanceResponse,
)
async def advance_simulation(
    mission_id: UUID,
    payload: SimulationAdvanceRequest,
    session: SessionDependency,
) -> SimulationAdvanceResponse:
    service = SimulationService(session)

    simulation = await service.get(mission_id)

    runtime = await service.advance(
        mission_id,
        real_duration_s=payload.real_duration_s,
    )

    if settings.messaging_enabled:
        await publish_simulation_state(
            event_bus=event_bus,
            simulation=simulation,
            runtime=runtime,
        )

    return SimulationAdvanceResponse(
        simulated_duration_s=(payload.real_duration_s * simulation.simulation_speed),
        state=simulation_state_response(runtime),
    )


@router.get(
    "/{mission_id}/state",
    response_model=SimulationStateResponse,
)
async def get_simulation_state(
    mission_id: UUID,
    session: SessionDependency,
) -> SimulationStateResponse:
    runtime = await SimulationService(session).get_state(mission_id)

    return simulation_state_response(runtime)


@router.get(
    "/{mission_id}/checkpoints",
    response_model=list[SimulationCheckpointResponse],
)
async def get_simulation_checkpoints(
    mission_id: UUID,
    session: SessionDependency,
) -> list[SimulationCheckpointResponse]:
    checkpoints = await SimulationService(session).get_checkpoints(mission_id)

    return [SimulationCheckpointResponse.model_validate(checkpoint) for checkpoint in checkpoints]
