from app.core.config import Settings
from app.domain.enums import (
    AlertSeverity,
    AlertType,
    RecommendationType,
)
from app.schemas.alerts import DetectedAnomaly
from app.schemas.telemetry import TelemetryPoint


class SafetyService:
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self._settings = settings

    def evaluate(
        self,
        telemetry: TelemetryPoint,
    ) -> list[DetectedAnomaly]:
        anomalies: list[DetectedAnomaly] = []

        self._evaluate_propellant(
            telemetry,
            anomalies,
        )

        self._evaluate_oxygen(
            telemetry,
            anomalies,
        )

        self._evaluate_power(
            telemetry,
            anomalies,
        )

        self._evaluate_communication(
            telemetry,
            anomalies,
        )

        self._evaluate_trajectory(
            telemetry,
            anomalies,
        )

        return anomalies

    def _evaluate_propellant(
        self,
        telemetry: TelemetryPoint,
        anomalies: list[DetectedAnomaly],
    ) -> None:
        value = telemetry.propulsion.propellant_percent

        if value <= self._settings.propellant_critical_percent:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=(AlertType.PROPELLANT_RESERVE_VIOLATION),
                    severity=AlertSeverity.CRITICAL,
                    message=("Propellant reserve is below the critical safety threshold."),
                    measured_value=value,
                    threshold=(self._settings.propellant_critical_percent),
                    recommendation=(RecommendationType.RETURN_TO_EARTH),
                )
            )
            return

        if value <= self._settings.propellant_low_percent:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=(AlertType.LOW_PROPELLANT),
                    severity=AlertSeverity.WARNING,
                    message=("Remaining propellant is below the configured warning threshold."),
                    measured_value=value,
                    threshold=(self._settings.propellant_low_percent),
                )
            )

    def _evaluate_oxygen(
        self,
        telemetry: TelemetryPoint,
        anomalies: list[DetectedAnomaly],
    ) -> None:
        value = telemetry.life_support.oxygen_percent

        if value <= self._settings.oxygen_critical_percent:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=AlertType.OXYGEN_CRITICAL,
                    severity=AlertSeverity.CRITICAL,
                    message=("Oxygen level is below the critical safety threshold."),
                    measured_value=value,
                    threshold=(self._settings.oxygen_critical_percent),
                    recommendation=(RecommendationType.RETURN_TO_EARTH),
                )
            )
            return

        if value <= self._settings.oxygen_low_percent:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=AlertType.OXYGEN_LOW,
                    severity=AlertSeverity.WARNING,
                    message=("Oxygen level is below the configured warning threshold."),
                    measured_value=value,
                    threshold=(self._settings.oxygen_low_percent),
                )
            )

    def _evaluate_power(
        self,
        telemetry: TelemetryPoint,
        anomalies: list[DetectedAnomaly],
    ) -> None:
        value = telemetry.power.battery_percent

        if value <= self._settings.battery_critical_percent:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=AlertType.POWER_LOW,
                    severity=AlertSeverity.CRITICAL,
                    message=("Available battery energy is below the critical safety threshold."),
                    measured_value=value,
                    threshold=(self._settings.battery_critical_percent),
                    recommendation=(RecommendationType.RETURN_TO_EARTH),
                )
            )
            return

        if value <= self._settings.battery_low_percent:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=AlertType.POWER_LOW,
                    severity=AlertSeverity.WARNING,
                    message=("Available battery energy is below the configured warning threshold."),
                    measured_value=value,
                    threshold=(self._settings.battery_low_percent),
                )
            )

    def _evaluate_communication(
        self,
        telemetry: TelemetryPoint,
        anomalies: list[DetectedAnomaly],
    ) -> None:
        communication = telemetry.communication

        if communication is None:
            return

        if communication.signal_status == "LOST":
            anomalies.append(
                DetectedAnomaly(
                    alert_type=(AlertType.COMMUNICATION_LOST),
                    severity=AlertSeverity.CRITICAL,
                    message=("Communication with the spacecraft has been lost."),
                    measured_value="LOST",
                    threshold="AVAILABLE_OR_DEGRADED",
                )
            )
            return

        if (
            communication.signal_status == "DEGRADED"
            or communication.packet_loss_percent
            >= self._settings.communication_packet_loss_warning_percent
        ):
            anomalies.append(
                DetectedAnomaly(
                    alert_type=(AlertType.COMMUNICATION_DEGRADED),
                    severity=AlertSeverity.WARNING,
                    message=("Communication quality is degraded."),
                    measured_value=(communication.packet_loss_percent),
                    threshold=(self._settings.communication_packet_loss_warning_percent),
                )
            )

    def _evaluate_trajectory(
        self,
        telemetry: TelemetryPoint,
        anomalies: list[DetectedAnomaly],
    ) -> None:
        deviation = telemetry.navigation.trajectory_deviation_km

        if deviation is None:
            return

        absolute_deviation = abs(deviation)

        if absolute_deviation >= self._settings.trajectory_deviation_critical_km:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=(AlertType.TRAJECTORY_DEVIATION),
                    severity=AlertSeverity.CRITICAL,
                    message=("Spacecraft trajectory deviation exceeds the critical threshold."),
                    measured_value=(absolute_deviation),
                    threshold=(self._settings.trajectory_deviation_critical_km),
                    recommendation=(RecommendationType.CORRECTIVE_MANEUVER),
                )
            )
            return

        if absolute_deviation >= self._settings.trajectory_deviation_warning_km:
            anomalies.append(
                DetectedAnomaly(
                    alert_type=(AlertType.TRAJECTORY_DEVIATION),
                    severity=AlertSeverity.WARNING,
                    message=("Spacecraft trajectory deviation exceeds the warning threshold."),
                    measured_value=(absolute_deviation),
                    threshold=(self._settings.trajectory_deviation_warning_km),
                    recommendation=(RecommendationType.CORRECTIVE_MANEUVER),
                )
            )
