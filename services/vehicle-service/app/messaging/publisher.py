import logging

from smc_messaging import (
    EventBus,
    EventEnvelope,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

event_bus = EventBus(
    nats_url=settings.nats_url,
    client_name=settings.service_name,
)


async def publish_event(
    *,
    subject: str,
    envelope: EventEnvelope,
) -> None:
    await event_bus.publish(
        subject=subject,
        envelope=envelope,
    )
