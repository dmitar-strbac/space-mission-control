from uuid import uuid4

import pytest
from smc_messaging import EventEnvelope
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.idempotency_service import IdempotencyService


@pytest.mark.asyncio
async def test_processed_event_is_persisted(
    session: AsyncSession,
) -> None:
    event = EventEnvelope.create(
        event_type="test.event",
        source="test-service",
        correlation_id=str(uuid4()),
        payload={},
    )

    service = IdempotencyService(session)

    assert not await service.was_processed(event)

    await service.mark_processed(event)

    assert await service.was_processed(event)
