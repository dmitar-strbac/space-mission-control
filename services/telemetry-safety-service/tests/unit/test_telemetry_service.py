from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.telemetry import EARTH_RADIUS_M
from app.schemas.communication import CommunicationStatusEventPayload
from app.schemas.simulation import (
    SimulationStateEventPayload,
    Vector2DInput,
)
from app.services.telemetry_service import TelemetryService


def _simulation_state() -> SimulationStateEventPayload:
    return SimulationStateEventPayload(
        mission_id=uuid4(),
        simulation_session_id=uuid4(),
        simulation_time_s=120.0,
        position=Vector2DInput(
            x=EARTH_RADIUS_M + 400_000.0,
            y=0.0,
        ),
        velocity=Vector2DInput(
            x=0.0,
            y=7_670.0,
        ),
        total_mass_kg=10_000.0,
        propellant_kg=2_000.0,
        initial_propellant_kg=4_000.0,
        oxygen_kg=80.0,
        initial_oxygen_kg=100.0,
        oxygen_consumption_rate_kg_s=0.001,
        battery_kwh=75.0,
        initial_battery_kwh=100.0,
        power_consumption_kw=10.0,
        engine_thrust_n=0.0,
        engine_specific_impulse_s=320.0,
        active_maneuver_id=None,
    )


def test_process_state_derives_physical_telemetry() -> None:
    telemetry = TelemetryService().process_state(_simulation_state())

    assert telemetry.navigation.altitude_km == pytest.approx(400.0)
    assert telemetry.navigation.speed_km_s == pytest.approx(7.67)
    assert telemetry.navigation.vertical_speed_m_s == pytest.approx(0.0)

    assert telemetry.propulsion.propellant_percent == pytest.approx(50.0)

    assert telemetry.life_support.oxygen_percent == pytest.approx(80.0)

    assert telemetry.power.battery_percent == pytest.approx(75.0)

    assert telemetry.communication is None


def test_process_state_includes_latest_communication_status() -> None:
    state = _simulation_state()

    communication = CommunicationStatusEventPayload(
        mission_id=state.mission_id,
        signal_status="DEGRADED",
        one_way_delay_ms=42.0,
        packet_loss_percent=15.0,
        observed_at=datetime.now(UTC),
    )

    telemetry = TelemetryService().process_state(
        state,
        communication=communication,
    )

    assert telemetry.communication is not None

    assert telemetry.communication.signal_status == "DEGRADED"
    assert telemetry.communication.one_way_delay_ms == pytest.approx(42.0)
    assert telemetry.communication.packet_loss_percent == pytest.approx(15.0)
