import random
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.command import can_transition
from app.domain.communication import (
    calculate_communication_delay,
    can_transmit,
    should_lose_packet,
)
from app.domain.enums import CommandStatus
from app.domain.exceptions import (
    CommandDeliveryError,
    CommandNotFoundError,
    CommunicationProfileNotFoundError,
    InvalidCommandTransitionError,
)
from app.models.command import Command
from app.models.command_log import CommandLog
from app.repositories.command_repository import CommandRepository
from app.repositories.communication_profile_repository import (
    CommunicationProfileRepository,
)
from app.schemas.command import CommandCreateRequest


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


class CommandService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._commands = CommandRepository(session)
        self._profiles = CommunicationProfileRepository(session)

    async def create(
        self,
        request: CommandCreateRequest,
    ) -> Command:
        profile = await self._profiles.get_by_mission_id(request.mission_id)

        if profile is None:
            raise CommunicationProfileNotFoundError(request.mission_id)

        command = Command(
            mission_id=request.mission_id,
            command_type=request.command_type,
            payload=request.payload,
            status=CommandStatus.CREATED,
        )

        self._commands.add(command)

        await self._session.flush()

        self._commands.add_log(
            CommandLog(
                command_id=command.id,
                previous_status=None,
                new_status=CommandStatus.CREATED,
                message="Command created.",
            )
        )

        await self._session.commit()

        return await self.get(command.id)

    async def get(
        self,
        command_id: UUID,
    ) -> Command:
        command = await self._commands.get_by_id(command_id)

        if command is None:
            raise CommandNotFoundError(command_id)

        return command

    async def list_for_mission(
        self,
        mission_id: UUID,
    ) -> Sequence[Command]:
        return await self._commands.list_by_mission_id(mission_id)

    async def get_logs(
        self,
        command_id: UUID,
    ) -> Sequence[CommandLog]:
        await self.get(command_id)

        return await self._commands.get_logs(command_id)

    async def queue(
        self,
        command_id: UUID,
    ) -> Command:
        return await self._transition(
            command_id=command_id,
            target=CommandStatus.QUEUED,
            message="Command queued for transmission.",
        )

    async def dispatch(
        self,
        command_id: UUID,
        *,
        packet_sample: float | None = None,
    ) -> tuple[Command, float]:
        command = await self._commands.get_by_id(
            command_id,
            for_update=True,
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        if command.status is not CommandStatus.QUEUED:
            raise InvalidCommandTransitionError(
                (
                    f"Command '{command.id}' cannot be dispatched "
                    f"from status '{command.status.value}'."
                ),
                details={
                    "command_id": str(command.id),
                    "current_status": command.status.value,
                    "target_status": CommandStatus.IN_TRANSIT.value,
                },
            )

        profile = await self._profiles.get_by_mission_id(command.mission_id)

        if profile is None:
            raise CommunicationProfileNotFoundError(command.mission_id)

        if not can_transmit(profile.signal_status):
            command = await self._apply_transition(
                command=command,
                target=CommandStatus.LOST,
                message="Command lost because communication signal is unavailable.",
            )

            await self._session.commit()

            raise CommandDeliveryError(
                "Command could not be transmitted because communication signal is lost.",
                details={
                    "command_id": str(command.id),
                    "mission_id": str(command.mission_id),
                },
            )

        sample = packet_sample if packet_sample is not None else random.random()

        if should_lose_packet(
            packet_loss_percent=profile.packet_loss_percent,
            sample=sample,
        ):
            command = await self._apply_transition(
                command=command,
                target=CommandStatus.LOST,
                message="Command packet was lost during transmission.",
            )

            await self._session.commit()

            raise CommandDeliveryError(
                "Command packet was lost during transmission.",
                details={
                    "command_id": str(command.id),
                    "mission_id": str(command.mission_id),
                },
            )

        delay = calculate_communication_delay(
            distance_m=profile.distance_m,
            additional_latency_ms=(profile.additional_latency_ms),
        )

        now = datetime.now(UTC)

        command.scheduled_delivery_at = now + timedelta(seconds=delay.total_delay_s)

        await self._apply_transition(
            command=command,
            target=CommandStatus.IN_TRANSIT,
            message=(
                "Command entered transmission. "
                f"Estimated one-way delay: "
                f"{delay.total_delay_s * 1000:.3f} ms."
            ),
        )

        await self._session.commit()
        await self._session.refresh(command)

        return command, delay.total_delay_s * 1000.0

    async def deliver(
        self,
        command_id: UUID,
        *,
        current_time: datetime | None = None,
    ) -> Command:
        command = await self._commands.get_by_id(
            command_id,
            for_update=True,
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        if command.status is not CommandStatus.IN_TRANSIT:
            raise InvalidCommandTransitionError(
                (
                    f"Command '{command.id}' cannot be delivered "
                    f"from status '{command.status.value}'."
                ),
                details={
                    "command_id": str(command.id),
                    "current_status": command.status.value,
                    "target_status": CommandStatus.DELIVERED.value,
                },
            )

        now = _ensure_utc(current_time or datetime.now(UTC))

        scheduled_delivery_at = command.scheduled_delivery_at

        if scheduled_delivery_at is None:
            raise CommandDeliveryError(
                "Command has no scheduled delivery time.",
                details={
                    "command_id": str(command.id),
                },
            )

        scheduled_delivery_at = _ensure_utc(scheduled_delivery_at)

        if now < scheduled_delivery_at:
            raise CommandDeliveryError(
                "Command has not yet reached its scheduled delivery time.",
                details={
                    "command_id": str(command.id),
                    "scheduled_delivery_at": (scheduled_delivery_at.isoformat()),
                },
            )

        command.received_at = now

        await self._apply_transition(
            command=command,
            target=CommandStatus.DELIVERED,
            message="Command delivered to spacecraft.",
        )

        await self._session.commit()
        await self._session.refresh(command)

        return command

    async def execute(
        self,
        command_id: UUID,
    ) -> Command:
        command = await self._commands.get_by_id(
            command_id,
            for_update=True,
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        if command.status is not CommandStatus.DELIVERED:
            raise InvalidCommandTransitionError(
                (
                    f"Command '{command.id}' cannot be executed "
                    f"from status '{command.status.value}'."
                ),
                details={
                    "command_id": str(command.id),
                    "current_status": command.status.value,
                    "target_status": CommandStatus.EXECUTED.value,
                },
            )

        command.executed_at = datetime.now(UTC)

        await self._apply_transition(
            command=command,
            target=CommandStatus.EXECUTED,
            message="Command execution confirmed.",
        )

        await self._session.commit()
        await self._session.refresh(command)

        return command

    async def reject(
        self,
        command_id: UUID,
        *,
        reason: str,
    ) -> Command:
        command = await self._commands.get_by_id(
            command_id,
            for_update=True,
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        command.rejection_reason = reason

        await self._apply_transition(
            command=command,
            target=CommandStatus.REJECTED,
            message=reason,
        )

        await self._session.commit()
        await self._session.refresh(command)

        return command

    async def expire(
        self,
        command_id: UUID,
    ) -> Command:
        return await self._transition(
            command_id=command_id,
            target=CommandStatus.EXPIRED,
            message="Command expired before successful execution.",
        )

    async def mark_lost(
        self,
        command_id: UUID,
    ) -> Command:
        return await self._transition(
            command_id=command_id,
            target=CommandStatus.LOST,
            message="Command marked as lost.",
        )

    async def _transition(
        self,
        *,
        command_id: UUID,
        target: CommandStatus,
        message: str,
    ) -> Command:
        command = await self._commands.get_by_id(
            command_id,
            for_update=True,
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        await self._apply_transition(
            command=command,
            target=target,
            message=message,
        )

        await self._session.commit()
        await self._session.refresh(command)

        return command

    async def _apply_transition(
        self,
        *,
        command: Command,
        target: CommandStatus,
        message: str,
    ) -> Command:
        previous_status = command.status

        if not can_transition(
            previous_status,
            target,
        ):
            raise InvalidCommandTransitionError(
                (
                    f"Command '{command.id}' cannot transition "
                    f"from '{previous_status.value}' "
                    f"to '{target.value}'."
                ),
                details={
                    "command_id": str(command.id),
                    "current_status": previous_status.value,
                    "target_status": target.value,
                },
            )

        command.status = target

        self._commands.add_log(
            CommandLog(
                command_id=command.id,
                previous_status=previous_status,
                new_status=target,
                message=message,
            )
        )

        return command
