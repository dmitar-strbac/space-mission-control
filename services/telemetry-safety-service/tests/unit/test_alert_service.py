from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.enums import (
    AlertSeverity,
    AlertType,
)
from app.schemas.alerts import (
    AlertRecord,
    AnomalyEvent,
    DetectedAnomaly,
)
from app.schemas.telemetry import (
    LifeSupportTelemetry,
    NavigationTelemetry,
    PowerTelemetry,
    PropulsionTelemetry,
    TelemetryPoint,
)
from app.services.alert_service import AlertService


class FakeAlertRepository:
    def __init__(self) -> None:
        self.alerts: list[AlertRecord] = []

    async def create(
        self,
        alert: AlertRecord,
    ) -> None:
        self.alerts.append(alert)

    async def get_active(
        self,
        *,
        mission_id: UUID,
        alert_type: AlertType,
    ) -> AlertRecord | None:
        return next(
            (
                alert
                for alert in self.alerts
                if alert.mission_id == mission_id
                and alert.alert_type == alert_type
                and alert.resolved_at is None
            ),
            None,
        )

    async def update_active(
        self,
        alert: AlertRecord,
    ) -> None:
        return None

    async def resolve_absent(
        self,
        *,
        mission_id: UUID,
        active_types: set[AlertType],
        resolved_at: datetime,
    ) -> None:
        for alert in self.alerts:
            if (
                alert.mission_id == mission_id
                and alert.resolved_at is None
                and alert.alert_type not in active_types
            ):
                alert.resolved_at = resolved_at


class FakeAnomalyRepository:
    def __init__(self) -> None:
        self.events: list[AnomalyEvent] = []

    async def create(
        self,
        anomaly: AnomalyEvent,
    ) -> None:
        self.events.append(anomaly)


def _telemetry() -> TelemetryPoint:
    return TelemetryPoint(
        mission_id=uuid4(),
        simulation_session_id=uuid4(),
        simulation_time_s=100.0,
        recorded_at=datetime.now(UTC),
        navigation=NavigationTelemetry(
            altitude_km=400.0,
            speed_km_s=7.67,
            vertical_speed_m_s=0.0,
        ),
        propulsion=PropulsionTelemetry(
            propellant_kg=100.0,
            propellant_percent=10.0,
            fuel_flow_kg_s=0.0,
            engine_thrust_n=0.0,
            remaining_delta_v_m_s=100.0,
        ),
        life_support=LifeSupportTelemetry(
            oxygen_kg=80.0,
            oxygen_percent=80.0,
            crew_consumption_rate_kg_s=0.001,
            estimated_oxygen_remaining_h=20.0,
        ),
        power=PowerTelemetry(
            battery_kwh=80.0,
            battery_percent=80.0,
            power_consumption_kw=5.0,
            estimated_power_remaining_h=16.0,
        ),
    )


def _warning() -> DetectedAnomaly:
    return DetectedAnomaly(
        alert_type=AlertType.LOW_PROPELLANT,
        severity=AlertSeverity.WARNING,
        message="Propellant is low.",
        measured_value=15.0,
        threshold=20.0,
    )


async def test_new_anomaly_creates_alert_and_anomaly_event() -> None:
    alert_repository = FakeAlertRepository()
    anomaly_repository = FakeAnomalyRepository()

    service = AlertService(
        alert_repository=alert_repository,
        anomaly_repository=anomaly_repository,
    )

    actionable = await service.synchronize(
        telemetry=_telemetry(),
        anomalies=[_warning()],
    )

    assert len(alert_repository.alerts) == 1
    assert len(anomaly_repository.events) == 1
    assert len(actionable) == 1


async def test_repeated_anomaly_does_not_create_duplicate_alert() -> None:
    alert_repository = FakeAlertRepository()
    anomaly_repository = FakeAnomalyRepository()

    service = AlertService(
        alert_repository=alert_repository,
        anomaly_repository=anomaly_repository,
    )

    telemetry = _telemetry()
    anomaly = _warning()

    await service.synchronize(
        telemetry=telemetry,
        anomalies=[anomaly],
    )

    actionable = await service.synchronize(
        telemetry=telemetry,
        anomalies=[anomaly],
    )

    assert len(alert_repository.alerts) == 1
    assert len(anomaly_repository.events) == 1
    assert actionable == []


async def test_disappearing_condition_resolves_active_alert() -> None:
    alert_repository = FakeAlertRepository()
    anomaly_repository = FakeAnomalyRepository()

    service = AlertService(
        alert_repository=alert_repository,
        anomaly_repository=anomaly_repository,
    )

    telemetry = _telemetry()

    await service.synchronize(
        telemetry=telemetry,
        anomalies=[_warning()],
    )

    await service.synchronize(
        telemetry=telemetry,
        anomalies=[],
    )

    assert alert_repository.alerts[0].resolved_at is not None
