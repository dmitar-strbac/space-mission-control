from smc_messaging import EventEnvelope
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.processed_event_repository import (
    ProcessedEventRepository,
)


class IdempotencyService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._repository = ProcessedEventRepository(session)

    async def was_processed(
        self,
        envelope: EventEnvelope,
    ) -> bool:
        return await self._repository.exists(envelope.event_id)

    async def mark_processed(
        self,
        envelope: EventEnvelope,
    ) -> None:
        self._repository.add(
            event_id=envelope.event_id,
            event_type=envelope.event_type,
        )

        await self._session.commit()
