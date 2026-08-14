from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import Settings
from app.domain.enums import (
    AlertSeverity,
    AlertType,
    RecommendationType,
)
from app.schemas.telemetry import (
    CommunicationTelemetry,
    LifeSupportTelemetry,
    NavigationTelemetry,
    PowerTelemetry,
    PropulsionTelemetry,
    TelemetryPoint,
)
from app.services.safety_service import SafetyService


def _telemetry(
    *,
    propellant_percent: float = 80.0,
    oxygen_percent: float = 80.0,
    battery_percent: float = 80.0,
    communication: CommunicationTelemetry | None = None,
    trajectory_deviation_km: float | None = None,
) -> TelemetryPoint:
    return TelemetryPoint(
        mission_id=uuid4(),
        simulation_session_id=uuid4(),
        simulation_time_s=100.0,
        recorded_at=datetime.now(UTC),
        navigation=NavigationTelemetry(
            altitude_km=400.0,
            speed_km_s=7.67,
            vertical_speed_m_s=0.0,
            trajectory_deviation_km=(trajectory_deviation_km),
        ),
        propulsion=PropulsionTelemetry(
            propellant_kg=800.0,
            propellant_percent=propellant_percent,
            fuel_flow_kg_s=0.0,
            engine_thrust_n=0.0,
            remaining_delta_v_m_s=1_000.0,
        ),
        life_support=LifeSupportTelemetry(
            oxygen_kg=80.0,
            oxygen_percent=oxygen_percent,
            crew_consumption_rate_kg_s=0.001,
            estimated_oxygen_remaining_h=20.0,
        ),
        power=PowerTelemetry(
            battery_kwh=80.0,
            battery_percent=battery_percent,
            power_consumption_kw=5.0,
            estimated_power_remaining_h=16.0,
        ),
        communication=communication,
    )


def test_nominal_telemetry_produces_no_anomalies() -> None:
    anomalies = SafetyService(Settings()).evaluate(_telemetry())

    assert anomalies == []


def test_low_propellant_produces_warning() -> None:
    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            propellant_percent=15.0,
        )
    )

    assert len(anomalies) == 1

    anomaly = anomalies[0]

    assert anomaly.alert_type is AlertType.LOW_PROPELLANT
    assert anomaly.severity is AlertSeverity.WARNING
    assert anomaly.recommendation is None


def test_critical_propellant_recommends_return() -> None:
    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            propellant_percent=5.0,
        )
    )

    assert len(anomalies) == 1

    anomaly = anomalies[0]

    assert anomaly.alert_type is AlertType.PROPELLANT_RESERVE_VIOLATION
    assert anomaly.severity is AlertSeverity.CRITICAL
    assert anomaly.recommendation is RecommendationType.RETURN_TO_EARTH


def test_critical_oxygen_recommends_return() -> None:
    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            oxygen_percent=5.0,
        )
    )

    oxygen = next(
        anomaly for anomaly in anomalies if anomaly.alert_type is AlertType.OXYGEN_CRITICAL
    )

    assert oxygen.severity is AlertSeverity.CRITICAL
    assert oxygen.recommendation is RecommendationType.RETURN_TO_EARTH


def test_low_power_produces_warning() -> None:
    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            battery_percent=15.0,
        )
    )

    power = next(anomaly for anomaly in anomalies if anomaly.alert_type is AlertType.POWER_LOW)

    assert power.severity is AlertSeverity.WARNING


def test_lost_communication_produces_critical_alert() -> None:
    communication = CommunicationTelemetry(
        signal_status="LOST",
        one_way_delay_ms=100.0,
        packet_loss_percent=100.0,
        last_contact_at=None,
    )

    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            communication=communication,
        )
    )

    communication_anomaly = next(
        anomaly for anomaly in anomalies if anomaly.alert_type is AlertType.COMMUNICATION_LOST
    )

    assert communication_anomaly.severity is AlertSeverity.CRITICAL


def test_packet_loss_produces_degraded_communication_alert() -> None:
    communication = CommunicationTelemetry(
        signal_status="AVAILABLE",
        one_way_delay_ms=20.0,
        packet_loss_percent=25.0,
        last_contact_at=datetime.now(UTC),
    )

    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            communication=communication,
        )
    )

    assert any(anomaly.alert_type is AlertType.COMMUNICATION_DEGRADED for anomaly in anomalies)


def test_trajectory_deviation_recommends_correction() -> None:
    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            trajectory_deviation_km=8.0,
        )
    )

    trajectory = next(
        anomaly for anomaly in anomalies if anomaly.alert_type is AlertType.TRAJECTORY_DEVIATION
    )

    assert trajectory.severity is AlertSeverity.WARNING
    assert trajectory.recommendation is RecommendationType.CORRECTIVE_MANEUVER


def test_critical_threshold_takes_precedence_over_warning() -> None:
    anomalies = SafetyService(Settings()).evaluate(
        _telemetry(
            oxygen_percent=5.0,
        )
    )

    oxygen_types = {
        anomaly.alert_type
        for anomaly in anomalies
        if anomaly.alert_type
        in {
            AlertType.OXYGEN_LOW,
            AlertType.OXYGEN_CRITICAL,
        }
    }

    assert oxygen_types == {AlertType.OXYGEN_CRITICAL}
