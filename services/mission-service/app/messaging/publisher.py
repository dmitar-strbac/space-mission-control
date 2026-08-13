import logging
from typing import Protocol

from smc_messaging import EventBus, EventEnvelope

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

event_bus = EventBus(
    nats_url=settings.nats_url,
    client_name=settings.service_name,
)


class EventPublisher(Protocol):
    async def publish(
        self,
        *,
        subject: str,
        envelope: EventEnvelope,
    ) -> None: ...


class NoOpEventPublisher:
    async def publish(
        self,
        *,
        subject: str,
        envelope: EventEnvelope,
    ) -> None:
        logger.debug(
            "Messaging disabled; skipping event %s on %s",
            envelope.event_type,
            subject,
        )


_no_op_publisher = NoOpEventPublisher()


def get_event_publisher() -> EventPublisher:
    if settings.messaging_enabled:
        return event_bus

    return _no_op_publisher
