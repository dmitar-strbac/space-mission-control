from collections.abc import Awaitable, Callable

from smc_messaging import (
    EventBus,
    EventEnvelope,
    SagaSubject,
)

from app.core.database import SessionFactory
from app.domain.enums import SagaStepType
from app.services.idempotency_service import IdempotencyService
from app.services.prepare_mission_saga import PrepareMissionSagaService

SagaHandler = Callable[
    [PrepareMissionSagaService, EventEnvelope],
    Awaitable[object],
]


async def _handle_once(
    envelope: EventEnvelope,
    handler: SagaHandler,
    event_bus: EventBus,
) -> None:
    async with SessionFactory() as session:
        idempotency = IdempotencyService(session)

        if await idempotency.was_processed(envelope):
            return

        service = PrepareMissionSagaService(
            session,
            event_bus,
        )

        await handler(
            service,
            envelope,
        )

        await idempotency.mark_processed(envelope)


async def register_saga_handlers(
    event_bus: EventBus,
) -> None:
    async def vehicle_reserved(
        envelope: EventEnvelope,
    ) -> None:
        await _handle_once(
            envelope,
            PrepareMissionSagaService.handle_vehicle_reserved,
            event_bus,
        )

    async def trajectory_created(
        envelope: EventEnvelope,
    ) -> None:
        await _handle_once(
            envelope,
            PrepareMissionSagaService.handle_trajectory_plan_created,
            event_bus,
        )

    async def resources_validated(
        envelope: EventEnvelope,
    ) -> None:
        await _handle_once(
            envelope,
            PrepareMissionSagaService.handle_resources_validated,
            event_bus,
        )

    async def communication_created(
        envelope: EventEnvelope,
    ) -> None:
        await _handle_once(
            envelope,
            PrepareMissionSagaService.handle_communication_profile_created,
            event_bus,
        )

    async def simulation_initialized(
        envelope: EventEnvelope,
    ) -> None:
        await _handle_once(
            envelope,
            PrepareMissionSagaService.handle_simulation_initialized,
            event_bus,
        )

    async def vehicle_rejected(
        envelope: EventEnvelope,
    ) -> None:
        async def handler(
            service: PrepareMissionSagaService,
            event: EventEnvelope,
        ) -> None:
            await service.handle_failure(
                event,
                failed_step=(SagaStepType.VEHICLE_RESERVATION),
            )

        await _handle_once(
            envelope,
            handler,
            event_bus,
        )

    async def trajectory_rejected(
        envelope: EventEnvelope,
    ) -> None:
        async def handler(
            service: PrepareMissionSagaService,
            event: EventEnvelope,
        ) -> None:
            await service.handle_failure(
                event,
                failed_step=(SagaStepType.TRAJECTORY_PLANNING),
            )

        await _handle_once(
            envelope,
            handler,
            event_bus,
        )

    async def resources_rejected(
        envelope: EventEnvelope,
    ) -> None:
        async def handler(
            service: PrepareMissionSagaService,
            event: EventEnvelope,
        ) -> None:
            await service.handle_failure(
                event,
                failed_step=(SagaStepType.RESOURCE_VALIDATION),
            )

        await _handle_once(
            envelope,
            handler,
            event_bus,
        )

    async def communication_rejected(
        envelope: EventEnvelope,
    ) -> None:
        async def handler(
            service: PrepareMissionSagaService,
            event: EventEnvelope,
        ) -> None:
            await service.handle_failure(
                event,
                failed_step=(SagaStepType.COMMUNICATION_PROFILE),
            )

        await _handle_once(
            envelope,
            handler,
            event_bus,
        )

    async def simulation_rejected(
        envelope: EventEnvelope,
    ) -> None:
        async def handler(
            service: PrepareMissionSagaService,
            event: EventEnvelope,
        ) -> None:
            await service.handle_failure(
                event,
                failed_step=(SagaStepType.SIMULATION_INITIALIZATION),
            )

        await _handle_once(
            envelope,
            handler,
            event_bus,
        )

    subscriptions = (
        (
            SagaSubject.VEHICLE_RESERVED,
            "mission-saga-vehicle-reserved",
            vehicle_reserved,
        ),
        (
            SagaSubject.TRAJECTORY_PLAN_CREATED,
            "mission-saga-trajectory-created",
            trajectory_created,
        ),
        (
            SagaSubject.RESOURCES_VALIDATED,
            "mission-saga-resources-validated",
            resources_validated,
        ),
        (
            SagaSubject.COMMUNICATION_PROFILE_CREATED,
            "mission-saga-communication-created",
            communication_created,
        ),
        (
            SagaSubject.SIMULATION_INITIALIZED,
            "mission-saga-simulation-initialized",
            simulation_initialized,
        ),
        (
            SagaSubject.VEHICLE_RESERVATION_REJECTED,
            "mission-saga-vehicle-rejected",
            vehicle_rejected,
        ),
        (
            SagaSubject.TRAJECTORY_PLAN_REJECTED,
            "mission-saga-trajectory-rejected",
            trajectory_rejected,
        ),
        (
            SagaSubject.RESOURCES_VALIDATION_REJECTED,
            "mission-saga-resources-rejected",
            resources_rejected,
        ),
        (
            SagaSubject.COMMUNICATION_PROFILE_REJECTED,
            "mission-saga-communication-rejected",
            communication_rejected,
        ),
        (
            SagaSubject.SIMULATION_INITIALIZATION_REJECTED,
            "mission-saga-simulation-rejected",
            simulation_rejected,
        ),
        (
            SagaSubject.VEHICLE_RELEASED,
            "mission-saga-vehicle-released",
            lambda event: _handle_once(
                event,
                PrepareMissionSagaService.handle_vehicle_released,
                event_bus,
            ),
        ),
        (
            SagaSubject.TRAJECTORY_PLAN_CANCELLED,
            "mission-saga-trajectory-cancelled",
            lambda event: _handle_once(
                event,
                PrepareMissionSagaService.handle_trajectory_cancelled,
                event_bus,
            ),
        ),
        (
            SagaSubject.COMMUNICATION_PROFILE_REMOVED,
            "mission-saga-communication-removed",
            lambda event: _handle_once(
                event,
                PrepareMissionSagaService.handle_communication_profile_removed,
                event_bus,
            ),
        ),
        (
            SagaSubject.SIMULATION_CLEANED,
            "mission-saga-simulation-cleaned",
            lambda event: _handle_once(
                event,
                PrepareMissionSagaService.handle_simulation_cleaned,
                event_bus,
            ),
        ),
    )

    for (
        subject,
        durable,
        handler,
    ) in subscriptions:
        await event_bus.subscribe(
            subject=subject.value,
            durable_name=durable,
            handler=handler,
        )
