from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.command import (
    CommandCreateRequest,
    CommandDispatchResponse,
    CommandLogResponse,
    CommandRejectRequest,
    CommandResponse,
)
from app.services.command_service import CommandService

router = APIRouter(
    tags=["Commands"],
)

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@router.post(
    "/commands",
    response_model=CommandResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_command(
    payload: CommandCreateRequest,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).create(payload)

    return CommandResponse.model_validate(command)


@router.get(
    "/commands/{command_id}",
    response_model=CommandResponse,
)
async def get_command(
    command_id: UUID,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).get(command_id)

    return CommandResponse.model_validate(command)


@router.get(
    "/missions/{mission_id}/commands",
    response_model=list[CommandResponse],
)
async def get_mission_commands(
    mission_id: UUID,
    session: SessionDependency,
) -> list[CommandResponse]:
    commands = await CommandService(session).list_for_mission(mission_id)

    return [CommandResponse.model_validate(command) for command in commands]


@router.get(
    "/commands/{command_id}/logs",
    response_model=list[CommandLogResponse],
)
async def get_command_logs(
    command_id: UUID,
    session: SessionDependency,
) -> list[CommandLogResponse]:
    logs = await CommandService(session).get_logs(command_id)

    return [CommandLogResponse.model_validate(log) for log in logs]


@router.post(
    "/commands/{command_id}/queue",
    response_model=CommandResponse,
)
async def queue_command(
    command_id: UUID,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).queue(command_id)

    return CommandResponse.model_validate(command)


@router.post(
    "/commands/{command_id}/dispatch",
    response_model=CommandDispatchResponse,
)
async def dispatch_command(
    command_id: UUID,
    session: SessionDependency,
) -> CommandDispatchResponse:
    command, one_way_delay_ms = await CommandService(session).dispatch(command_id)

    return CommandDispatchResponse(
        command=CommandResponse.model_validate(command),
        one_way_delay_ms=one_way_delay_ms,
    )


@router.post(
    "/commands/{command_id}/deliver",
    response_model=CommandResponse,
)
async def deliver_command(
    command_id: UUID,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).deliver(command_id)

    return CommandResponse.model_validate(command)


@router.post(
    "/commands/{command_id}/execute",
    response_model=CommandResponse,
)
async def execute_command(
    command_id: UUID,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).execute(command_id)

    return CommandResponse.model_validate(command)


@router.post(
    "/commands/{command_id}/reject",
    response_model=CommandResponse,
)
async def reject_command(
    command_id: UUID,
    payload: CommandRejectRequest,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).reject(
        command_id,
        reason=payload.reason,
    )

    return CommandResponse.model_validate(command)


@router.post(
    "/commands/{command_id}/expire",
    response_model=CommandResponse,
)
async def expire_command(
    command_id: UUID,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).expire(command_id)

    return CommandResponse.model_validate(command)


@router.post(
    "/commands/{command_id}/lost",
    response_model=CommandResponse,
)
async def mark_command_lost(
    command_id: UUID,
    session: SessionDependency,
) -> CommandResponse:
    command = await CommandService(session).mark_lost(command_id)

    return CommandResponse.model_validate(command)
