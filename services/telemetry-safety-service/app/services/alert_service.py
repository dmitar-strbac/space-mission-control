from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from app.domain.enums import AlertType
from app.schemas.alerts import (
    AlertRecord,
    AnomalyEvent,
    DetectedAnomaly,
)
from app.schemas.telemetry import TelemetryPoint


class AlertRepositoryProtocol(Protocol):
    async def create(
        self,
        alert: AlertRecord,
    ) -> None: ...

    async def get_active(
        self,
        *,
        mission_id: UUID,
        alert_type: AlertType,
    ) -> AlertRecord | None: ...

    async def update_active(
        self,
        alert: AlertRecord,
    ) -> None: ...

    async def resolve_absent(
        self,
        *,
        mission_id: UUID,
        active_types: set[AlertType],
        resolved_at: datetime,
    ) -> None: ...


class AnomalyRepositoryProtocol(Protocol):
    async def create(
        self,
        anomaly: AnomalyEvent,
    ) -> None: ...


class AlertService:
    def __init__(
        self,
        *,
        alert_repository: AlertRepositoryProtocol,
        anomaly_repository: AnomalyRepositoryProtocol,
    ) -> None:
        self._alerts = alert_repository
        self._anomalies = anomaly_repository

    async def synchronize(
        self,
        *,
        telemetry: TelemetryPoint,
        anomalies: list[DetectedAnomaly],
    ) -> list[
        tuple[
            AlertRecord,
            DetectedAnomaly,
        ]
    ]:
        now = datetime.now(UTC)

        newly_actionable: list[
            tuple[
                AlertRecord,
                DetectedAnomaly,
            ]
        ] = []

        active_types = {anomaly.alert_type for anomaly in anomalies}

        for anomaly in anomalies:
            existing = await self._alerts.get_active(
                mission_id=telemetry.mission_id,
                alert_type=anomaly.alert_type,
            )

            if existing is None:
                alert = AlertRecord(
                    mission_id=(telemetry.mission_id),
                    alert_type=(anomaly.alert_type),
                    severity=anomaly.severity,
                    message=anomaly.message,
                    measured_value=(anomaly.measured_value),
                    threshold=anomaly.threshold,
                    created_at=now,
                    last_seen_at=now,
                )

                await self._alerts.create(alert)

                anomaly_event = AnomalyEvent(
                    mission_id=(telemetry.mission_id),
                    alert_id=alert.id,
                    alert_type=(anomaly.alert_type),
                    severity=anomaly.severity,
                    measured_value=(anomaly.measured_value),
                    threshold=anomaly.threshold,
                    recommendation=(anomaly.recommendation),
                    created_at=now,
                )

                await self._anomalies.create(anomaly_event)

                newly_actionable.append(
                    (
                        alert,
                        anomaly,
                    )
                )

                continue

            severity_changed = existing.severity != anomaly.severity

            existing.severity = anomaly.severity
            existing.message = anomaly.message
            existing.measured_value = anomaly.measured_value
            existing.threshold = anomaly.threshold
            existing.last_seen_at = now

            await self._alerts.update_active(existing)

            if severity_changed:
                anomaly_event = AnomalyEvent(
                    mission_id=(telemetry.mission_id),
                    alert_id=existing.id,
                    alert_type=(anomaly.alert_type),
                    severity=anomaly.severity,
                    measured_value=(anomaly.measured_value),
                    threshold=anomaly.threshold,
                    recommendation=(anomaly.recommendation),
                    created_at=now,
                )

                await self._anomalies.create(anomaly_event)

                newly_actionable.append(
                    (
                        existing,
                        anomaly,
                    )
                )

        await self._alerts.resolve_absent(
            mission_id=telemetry.mission_id,
            active_types=active_types,
            resolved_at=now,
        )

        return newly_actionable
