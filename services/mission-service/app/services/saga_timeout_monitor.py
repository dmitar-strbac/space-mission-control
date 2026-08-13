import asyncio
import logging
from datetime import UTC, datetime, timedelta

from smc_messaging import EventEnvelope

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.messaging.publisher import event_bus
from app.repositories.saga_repository import SagaRepository
from app.services.prepare_mission_saga import PrepareMissionSagaService

logger = logging.getLogger(__name__)

settings = get_settings()


async def run_saga_timeout_monitor() -> None:
    while True:
        try:
            await _check_timeouts()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Prepare Mission Saga timeout monitor failed.")

        await asyncio.sleep(settings.saga_timeout_poll_interval_seconds)


async def _check_timeouts() -> None:
    cutoff = datetime.now(UTC) - timedelta(seconds=(settings.saga_step_timeout_seconds))

    async with SessionFactory() as session:
        repository = SagaRepository(session)

        timed_out = await repository.list_timed_out_steps(cutoff=cutoff)

        for step in timed_out:
            envelope = EventEnvelope.create(
                event_type="saga.step.timeout",
                source=settings.service_name,
                correlation_id=str(step.saga_id),
                causation_id=(step.request_event_id),
                payload={
                    "saga_id": str(step.saga_id),
                    "mission_id": str(step.mission_id),
                    "reason": (f"Saga step '{step.step_type.value}' timed out."),
                },
            )

            await PrepareMissionSagaService(
                session,
                event_bus,
            ).handle_failure(
                envelope,
                failed_step=step.step_type,
            )
