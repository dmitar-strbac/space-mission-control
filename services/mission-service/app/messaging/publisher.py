from typing import Protocol

from smc_messaging import EventEnvelope


class EventPublisher(Protocol):
    async def publish(
        self,
        *,
        subject: str,
        envelope: EventEnvelope,
    ) -> None: ...
