from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processed_event import ProcessedEvent


class ProcessedEventRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def exists(
        self,
        event_id: UUID,
    ) -> bool:
        statement = (
            select(ProcessedEvent.event_id).where(ProcessedEvent.event_id == event_id).limit(1)
        )

        result = await self._session.scalar(statement)

        return result is not None

    def add(
        self,
        *,
        event_id: UUID,
        event_type: str,
    ) -> None:
        self._session.add(
            ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
            )
        )
