from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import (
    CommandStatus,
    CommandType,
    SignalStatus,
)
from app.domain.exceptions import (
    CommandDeliveryError,
    InvalidCommandTransitionError,
)
from app.schemas.command import CommandCreateRequest
from app.schemas.communication_profile import CommunicationProfileCreateRequest
from app.services.command_service import CommandService
from app.services.communication_service import CommunicationService


async def _create_profile(
    session: AsyncSession,
    *,
    mission_id=None,
    distance_m: float = 0.0,
    packet_loss_percent: float = 0.0,
    signal_status: SignalStatus = SignalStatus.AVAILABLE,
):
    resolved_mission_id = mission_id or uuid4()

    await CommunicationService(session).create_profile(
        CommunicationProfileCreateRequest(
            mission_id=resolved_mission_id,
            distance_m=distance_m,
            additional_latency_ms=0.0,
            packet_loss_percent=packet_loss_percent,
            signal_status=signal_status,
        )
    )

    return resolved_mission_id


async def _create_command(
    session: AsyncSession,
    mission_id,
):
    return await CommandService(session).create(
        CommandCreateRequest(
            mission_id=mission_id,
            command_type=CommandType.PAUSE_SIMULATION,
            payload={},
        )
    )


@pytest.mark.asyncio
async def test_create_command_creates_initial_audit_log(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(session)

    service = CommandService(session)

    command = await service.create(
        CommandCreateRequest(
            mission_id=mission_id,
            command_type=CommandType.PAUSE_SIMULATION,
            payload={},
        )
    )

    assert command.status is CommandStatus.CREATED

    logs = await service.get_logs(command.id)

    assert len(logs) == 1
    assert logs[0].previous_status is None
    assert logs[0].new_status is CommandStatus.CREATED


@pytest.mark.asyncio
async def test_command_can_be_queued_and_dispatched(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(
        session,
        distance_m=400_000.0,
    )

    service = CommandService(session)

    command = await _create_command(
        session,
        mission_id,
    )

    command = await service.queue(command.id)

    assert command.status is CommandStatus.QUEUED

    command, delay_ms = await service.dispatch(
        command.id,
        packet_sample=0.5,
    )

    assert command.status is CommandStatus.IN_TRANSIT
    assert command.scheduled_delivery_at is not None
    assert delay_ms > 0.0


@pytest.mark.asyncio
async def test_command_can_complete_full_lifecycle(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(
        session,
        distance_m=0.0,
    )

    service = CommandService(session)

    command = await _create_command(
        session,
        mission_id,
    )

    await service.queue(command.id)

    command, _ = await service.dispatch(
        command.id,
        packet_sample=0.5,
    )

    assert command.scheduled_delivery_at is not None

    command = await service.deliver(
        command.id,
        current_time=(command.scheduled_delivery_at + timedelta(seconds=1)),
    )

    assert command.status is CommandStatus.DELIVERED
    assert command.received_at is not None

    command = await service.execute(command.id)

    assert command.status is CommandStatus.EXECUTED
    assert command.executed_at is not None

    logs = await service.get_logs(command.id)

    assert [log.new_status for log in logs] == [
        CommandStatus.CREATED,
        CommandStatus.QUEUED,
        CommandStatus.IN_TRANSIT,
        CommandStatus.DELIVERED,
        CommandStatus.EXECUTED,
    ]


@pytest.mark.asyncio
async def test_packet_loss_marks_command_as_lost(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(
        session,
        packet_loss_percent=100.0,
    )

    service = CommandService(session)

    command = await _create_command(
        session,
        mission_id,
    )

    await service.queue(command.id)

    with pytest.raises(CommandDeliveryError):
        await service.dispatch(
            command.id,
            packet_sample=0.5,
        )

    command = await service.get(command.id)

    assert command.status is CommandStatus.LOST

    logs = await service.get_logs(command.id)

    assert logs[-1].new_status is CommandStatus.LOST


@pytest.mark.asyncio
async def test_signal_loss_marks_command_as_lost(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(
        session,
        signal_status=SignalStatus.LOST,
    )

    service = CommandService(session)

    command = await _create_command(
        session,
        mission_id,
    )

    await service.queue(command.id)

    with pytest.raises(CommandDeliveryError):
        await service.dispatch(
            command.id,
            packet_sample=0.5,
        )

    command = await service.get(command.id)

    assert command.status is CommandStatus.LOST


@pytest.mark.asyncio
async def test_command_cannot_be_delivered_before_scheduled_time(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(
        session,
        distance_m=384_400_000.0,
    )

    service = CommandService(session)

    command = await _create_command(
        session,
        mission_id,
    )

    await service.queue(command.id)

    command, _ = await service.dispatch(
        command.id,
        packet_sample=0.5,
    )

    assert command.scheduled_delivery_at is not None

    too_early = command.scheduled_delivery_at - timedelta(milliseconds=1)

    with pytest.raises(CommandDeliveryError):
        await service.deliver(
            command.id,
            current_time=too_early,
        )


@pytest.mark.asyncio
async def test_invalid_transition_is_rejected(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(session)

    service = CommandService(session)

    command = await _create_command(
        session,
        mission_id,
    )

    with pytest.raises(InvalidCommandTransitionError):
        await service.execute(command.id)


@pytest.mark.asyncio
async def test_command_can_be_rejected(
    session: AsyncSession,
) -> None:
    mission_id = await _create_profile(session)

    service = CommandService(session)

    command = await _create_command(
        session,
        mission_id,
    )

    command = await service.reject(
        command.id,
        reason="Command payload failed validation.",
    )

    assert command.status is CommandStatus.REJECTED
    assert command.rejection_reason == "Command payload failed validation."
