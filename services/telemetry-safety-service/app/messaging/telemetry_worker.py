from smc_messaging import (
    EventBus,
    EventEnvelope,
    IntegrationSubject,
    LiveSubject,
)

from app.core.config import get_settings
from app.core.database import get_database
from app.messaging.safety_publisher import (
    publish_alert,
    publish_recommendation,
)
from app.repositories.alert_repository import AlertRepository
from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.schemas.communication import CommunicationStatusEventPayload
from app.schemas.simulation import SimulationStateEventPayload
from app.services.alert_service import AlertService
from app.services.communication_state_store import communication_state_store
from app.services.safety_service import SafetyService
from app.services.telemetry_service import TelemetryService
from app.services.websocket_manager import websocket_manager

settings = get_settings()


async def register_telemetry_worker(
    event_bus: EventBus,
) -> None:
    async def process_communication_status(
        envelope: EventEnvelope,
    ) -> None:
        state = CommunicationStatusEventPayload.model_validate(envelope.payload)

        communication_state_store.set(state)

    async def process_simulation_state(
        envelope: EventEnvelope,
    ) -> None:
        state = SimulationStateEventPayload.model_validate(envelope.payload)

        database = get_database()

        telemetry_repository = TelemetryRepository(database)

        alert_repository = AlertRepository(database)

        anomaly_repository = AnomalyRepository(database)

        communication = communication_state_store.get(state.mission_id)

        telemetry = TelemetryService().process_state(
            state,
            communication=communication,
        )

        await telemetry_repository.create(telemetry)

        processed_event = EventEnvelope.create(
            event_type=(LiveSubject.TELEMETRY_PROCESSED.value),
            source=settings.service_name,
            correlation_id=str(telemetry.mission_id),
            causation_id=(envelope.event_id),
            payload=telemetry.model_dump(mode="json"),
        )

        await event_bus.publish_ephemeral(
            subject=(LiveSubject.TELEMETRY_PROCESSED.value),
            envelope=processed_event,
        )

        await websocket_manager.broadcast_telemetry(telemetry)

        anomalies = SafetyService(settings).evaluate(telemetry)

        actionable_alerts = await AlertService(
            alert_repository=(alert_repository),
            anomaly_repository=(anomaly_repository),
        ).synchronize(
            telemetry=telemetry,
            anomalies=anomalies,
        )

        for alert, anomaly in actionable_alerts:
            await publish_alert(
                event_bus=event_bus,
                alert=alert,
            )

            await publish_recommendation(
                event_bus=event_bus,
                alert=alert,
                anomaly=anomaly,
            )

            await websocket_manager.broadcast_alert(alert)

    await event_bus.subscribe(
        subject=(IntegrationSubject.COMMUNICATION_STATUS_UPDATED.value),
        durable_name=("telemetry-communication-status-worker"),
        handler=process_communication_status,
    )

    await event_bus.subscribe_ephemeral(
        subject=(LiveSubject.SIMULATION_STATE_UPDATED.value),
        handler=process_simulation_state,
    )
