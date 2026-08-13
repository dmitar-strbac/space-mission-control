from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.command import Command
from app.models.command_log import CommandLog


class CommandRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(
        self,
        command: Command,
    ) -> None:
        self._session.add(command)

    def add_log(
        self,
        log: CommandLog,
    ) -> None:
        self._session.add(log)

    async def get_by_id(
        self,
        command_id: UUID,
        *,
        for_update: bool = False,
    ) -> Command | None:
        statement = (
            select(Command).options(selectinload(Command.logs)).where(Command.id == command_id)
        )

        if for_update:
            statement = statement.with_for_update()

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_mission_id(
        self,
        mission_id: UUID,
    ) -> Sequence[Command]:
        statement = (
            select(Command)
            .where(Command.mission_id == mission_id)
            .order_by(Command.issued_at.desc())
        )

        result = await self._session.execute(statement)

        return result.scalars().all()

    async def get_logs(
        self,
        command_id: UUID,
    ) -> Sequence[CommandLog]:
        statement = (
            select(CommandLog)
            .where(CommandLog.command_id == command_id)
            .order_by(CommandLog.occurred_at.asc())
        )

        result = await self._session.execute(statement)

        return result.scalars().all()
