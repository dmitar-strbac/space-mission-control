from collections.abc import Awaitable, Callable

from smc_messaging import EventBus, EventEnvelope, SagaSubject

from app.core.database import SessionFactory
from app.services.prepare_mission_saga import (
    PrepareMissionSagaService,
)


async def _handle(
    envelope: EventEnvelope,
    handler: Callable[
        [PrepareMissionSagaService, EventEnvelope],
        Awaitable[object],
    ],
    event_bus: EventBus,
) -> None:
    async with SessionFactory() as session:
        service = PrepareMissionSagaService(
            session,
            event_bus,
        )

        await handler(
            service,
            envelope,
        )


async def register_saga_handlers(
    event_bus: EventBus,
) -> None:
    async def vehicle_reserved(
        envelope: EventEnvelope,
    ) -> None:
        await _handle(
            envelope,
            PrepareMissionSagaService.handle_vehicle_reserved,
            event_bus,
        )

    async def trajectory_created(
        envelope: EventEnvelope,
    ) -> None:
        await _handle(
            envelope,
            PrepareMissionSagaService.handle_trajectory_plan_created,
            event_bus,
        )

    async def resources_validated(
        envelope: EventEnvelope,
    ) -> None:
        await _handle(
            envelope,
            PrepareMissionSagaService.handle_resources_validated,
            event_bus,
        )

    async def communication_created(
        envelope: EventEnvelope,
    ) -> None:
        await _handle(
            envelope,
            PrepareMissionSagaService.handle_communication_profile_created,
            event_bus,
        )

    async def simulation_initialized(
        envelope: EventEnvelope,
    ) -> None:
        await _handle(
            envelope,
            PrepareMissionSagaService.handle_simulation_initialized,
            event_bus,
        )

    await event_bus.subscribe(
        subject=SagaSubject.VEHICLE_RESERVED.value,
        durable_name="mission-saga-vehicle-reserved",
        handler=vehicle_reserved,
    )

    await event_bus.subscribe(
        subject=SagaSubject.TRAJECTORY_PLAN_CREATED.value,
        durable_name="mission-saga-trajectory-created",
        handler=trajectory_created,
    )

    await event_bus.subscribe(
        subject=SagaSubject.RESOURCES_VALIDATED.value,
        durable_name="mission-saga-resources-validated",
        handler=resources_validated,
    )

    await event_bus.subscribe(
        subject=SagaSubject.COMMUNICATION_PROFILE_CREATED.value,
        durable_name="mission-saga-communication-created",
        handler=communication_created,
    )

    await event_bus.subscribe(
        subject=SagaSubject.SIMULATION_INITIALIZED.value,
        durable_name="mission-saga-simulation-initialized",
        handler=simulation_initialized,
    )
