import logging
from collections.abc import Awaitable, Callable

import nats
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.aio.subscription import Subscription
from nats.js.client import JetStreamContext
from nats.js.errors import NotFoundError

from smc_messaging.envelope import EventEnvelope
from smc_messaging.subjects import (
    WORKFLOW_STREAM_NAME,
    WORKFLOW_STREAM_SUBJECTS,
)

logger = logging.getLogger(__name__)

EventHandler = Callable[
    [EventEnvelope],
    Awaitable[None],
]


class EventBus:
    def __init__(
        self,
        *,
        nats_url: str,
        client_name: str,
    ) -> None:
        self._nats_url = nats_url
        self._client_name = client_name

        self._connection: NATS | None = None
        self._jetstream: JetStreamContext | None = None

        self._subscriptions: list[Subscription] = []

    @property
    def connected(self) -> bool:
        return self._connection is not None and self._connection.is_connected

    async def connect(self) -> None:
        if self.connected:
            return

        self._connection = await nats.connect(
            servers=[self._nats_url],
            name=self._client_name,
        )

        self._jetstream = self._connection.jetstream()

        await self._ensure_workflow_stream()

        logger.info(
            "Connected %s to NATS at %s",
            self._client_name,
            self._nats_url,
        )

    async def close(self) -> None:
        for subscription in self._subscriptions:
            await subscription.unsubscribe()

        self._subscriptions.clear()

        if self._connection is not None:
            await self._connection.drain()

        self._connection = None
        self._jetstream = None

        logger.info(
            "Disconnected %s from NATS",
            self._client_name,
        )

    async def publish(
        self,
        *,
        subject: str,
        envelope: EventEnvelope,
    ) -> None:
        jetstream = self._require_jetstream()

        await jetstream.publish(
            subject,
            envelope.to_bytes(),
        )

        logger.info(
            "Published event %s to %s",
            envelope.event_type,
            subject,
        )

    async def subscribe(
        self,
        *,
        subject: str,
        durable_name: str,
        handler: EventHandler,
    ) -> Subscription:
        jetstream = self._require_jetstream()

        async def callback(
            message: Msg,
        ) -> None:
            try:
                envelope = EventEnvelope.from_bytes(message.data)

                await handler(envelope)

                await message.ack()

            except Exception:
                logger.exception(
                    "Failed processing message from subject %s",
                    message.subject,
                )

                await message.nak()

        subscription = await jetstream.subscribe(
            subject,
            durable=durable_name,
            cb=callback,
            manual_ack=True,
        )

        self._subscriptions.append(subscription)

        logger.info(
            "Subscribed %s to %s",
            durable_name,
            subject,
        )

        return subscription

    async def _ensure_workflow_stream(
        self,
    ) -> None:
        jetstream = self._require_jetstream()

        try:
            await jetstream.stream_info(WORKFLOW_STREAM_NAME)
        except NotFoundError:
            await jetstream.add_stream(
                name=WORKFLOW_STREAM_NAME,
                subjects=WORKFLOW_STREAM_SUBJECTS,
            )

            logger.info(
                "Created JetStream stream %s",
                WORKFLOW_STREAM_NAME,
            )

    def _require_jetstream(
        self,
    ) -> JetStreamContext:
        if self._jetstream is None:
            raise RuntimeError("Event bus is not connected.")

        return self._jetstream
