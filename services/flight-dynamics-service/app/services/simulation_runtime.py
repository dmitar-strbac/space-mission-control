import asyncio
import logging
from contextlib import suppress
from time import monotonic
from uuid import UUID

from app.core.config import get_settings
from app.core.database import SessionFactory
from app.domain.enums import SimulationStatus
from app.messaging.lifecycle_publisher import (
    publish_simulation_completed,
    publish_simulation_failed,
)
from app.messaging.publisher import event_bus
from app.messaging.state_publisher import publish_simulation_state
from app.services.simulation_service import SimulationService

logger = logging.getLogger(__name__)

settings = get_settings()


class SimulationRuntimeManager:
    def __init__(
        self,
        *,
        tick_interval_s: float = 1.0,
    ) -> None:
        self._tick_interval_s = tick_interval_s

        self._tasks: dict[
            UUID,
            asyncio.Task[None],
        ] = {}

        self.enabled = True

    def start(
        self,
        mission_id: UUID,
    ) -> None:
        if not self.enabled:
            return

        existing = self._tasks.get(mission_id)

        if existing is not None and not existing.done():
            return

        task = asyncio.create_task(
            self._run(mission_id),
            name=(f"simulation-runtime:{mission_id}"),
        )

        self._tasks[mission_id] = task

    async def stop(
        self,
        mission_id: UUID,
    ) -> None:
        task = self._tasks.pop(
            mission_id,
            None,
        )

        if task is None or task.done():
            return

        task.cancel()

        with suppress(asyncio.CancelledError):
            await task

    async def shutdown(
        self,
    ) -> None:
        tasks = list(self._tasks.values())

        self._tasks.clear()

        for task in tasks:
            if not task.done():
                task.cancel()

        for task in tasks:
            with suppress(asyncio.CancelledError):
                await task

    def is_running(
        self,
        mission_id: UUID,
    ) -> bool:
        task = self._tasks.get(mission_id)

        return task is not None and not task.done()

    async def _run(
        self,
        mission_id: UUID,
    ) -> None:
        current_task = asyncio.current_task()

        logger.info(
            ("Started autonomous simulation runtime for mission %s."),
            mission_id,
        )

        try:
            while True:
                tick_started_at = monotonic()

                async with SessionFactory() as session:
                    service = SimulationService(session)

                    simulation = await service.get(mission_id)

                    if simulation.status is not SimulationStatus.RUNNING:
                        return

                    runtime = await service.advance(
                        mission_id,
                        real_duration_s=(self._tick_interval_s),
                    )

                    simulation = await service.get(mission_id)

                    if settings.messaging_enabled:
                        await publish_simulation_state(
                            event_bus=event_bus,
                            simulation=simulation,
                            runtime=runtime,
                        )

                        if simulation.status is SimulationStatus.COMPLETED:
                            await publish_simulation_completed(
                                event_bus=event_bus,
                                simulation=simulation,
                                runtime=runtime,
                            )

                    if simulation.status is SimulationStatus.COMPLETED:
                        logger.info(
                            ("Simulation for mission %s completed."),
                            mission_id,
                        )

                        return

                tick_duration_s = monotonic() - tick_started_at

                sleep_duration_s = max(
                    0.0,
                    self._tick_interval_s - tick_duration_s,
                )

                await asyncio.sleep(sleep_duration_s)

        except asyncio.CancelledError:
            logger.info(
                ("Stopped autonomous simulation runtime for mission %s."),
                mission_id,
            )

            raise

        except Exception as error:
            logger.exception(
                ("Autonomous simulation runtime failed for mission %s."),
                mission_id,
            )

            if settings.messaging_enabled:
                try:
                    async with SessionFactory() as session:
                        simulation = await SimulationService(session).get(mission_id)

                    await publish_simulation_failed(
                        event_bus=event_bus,
                        mission_id=mission_id,
                        simulation_session_id=(simulation.id),
                        reason=str(error),
                    )

                except Exception:
                    logger.exception(
                        ("Failed to publish simulation failure for mission %s."),
                        mission_id,
                    )

        finally:
            stored_task = self._tasks.get(mission_id)

            if stored_task is current_task:
                self._tasks.pop(
                    mission_id,
                    None,
                )


simulation_runtime_manager = SimulationRuntimeManager()
