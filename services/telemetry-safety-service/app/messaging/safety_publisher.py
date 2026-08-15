from smc_messaging import (
    EventBus,
    EventEnvelope,
    SafetySubject,
)

from app.core.config import get_settings
from app.domain.enums import RecommendationType
from app.schemas.alerts import (
    AlertRecord,
    DetectedAnomaly,
)

settings = get_settings()


async def publish_alert(
    *,
    event_bus: EventBus,
    alert: AlertRecord,
) -> None:
    envelope = EventEnvelope.create(
        event_type=(SafetySubject.TELEMETRY_ALERT_CREATED.value),
        source=settings.service_name,
        correlation_id=str(alert.mission_id),
        payload=alert.model_dump(mode="json"),
    )

    await event_bus.publish(
        subject=(SafetySubject.TELEMETRY_ALERT_CREATED.value),
        envelope=envelope,
    )


async def publish_recommendation(
    *,
    event_bus: EventBus,
    alert: AlertRecord,
    anomaly: DetectedAnomaly,
) -> None:
    recommendation = anomaly.recommendation

    if recommendation is None:
        return

    subject_map = {
        RecommendationType.CORRECTIVE_MANEUVER: (SafetySubject.CORRECTIVE_MANEUVER_RECOMMENDED),
        RecommendationType.RETURN_TO_EARTH: (SafetySubject.RETURN_RECOMMENDED),
        RecommendationType.ABORT: (SafetySubject.ABORT_RECOMMENDED),
    }

    subject = subject_map[recommendation]

    envelope = EventEnvelope.create(
        event_type=subject.value,
        source=settings.service_name,
        correlation_id=str(alert.mission_id),
        payload={
            "mission_id": str(alert.mission_id),
            "alert_id": str(alert.id),
            "reason": alert.alert_type.value,
            "severity": alert.severity.value,
        },
    )

    await event_bus.publish(
        subject=subject.value,
        envelope=envelope,
    )
