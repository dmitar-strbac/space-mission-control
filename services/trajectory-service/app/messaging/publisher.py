from smc_messaging import EventBus

from app.core.config import get_settings

settings = get_settings()

event_bus = EventBus(
    nats_url=settings.nats_url,
    client_name=settings.service_name,
)
