from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.schemas.telemetry import (
    LifeSupportTelemetry,
    NavigationTelemetry,
    PowerTelemetry,
    PropulsionTelemetry,
    TelemetryPoint,
)
from app.services.websocket_manager import WebSocketManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.messages: list[dict[str, Any]] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(
        self,
        payload: dict[str, Any],
    ) -> None:
        self.messages.append(payload)


def _telemetry() -> TelemetryPoint:
    return TelemetryPoint(
        mission_id=uuid4(),
        simulation_session_id=uuid4(),
        simulation_time_s=10.0,
        recorded_at=datetime.now(UTC),
        navigation=NavigationTelemetry(
            altitude_km=400.0,
            speed_km_s=7.67,
            vertical_speed_m_s=0.0,
        ),
        propulsion=PropulsionTelemetry(
            propellant_kg=900.0,
            propellant_percent=90.0,
            fuel_flow_kg_s=0.0,
            engine_thrust_n=0.0,
            remaining_delta_v_m_s=1_000.0,
        ),
        life_support=LifeSupportTelemetry(
            oxygen_kg=90.0,
            oxygen_percent=90.0,
            crew_consumption_rate_kg_s=0.001,
            estimated_oxygen_remaining_h=20.0,
        ),
        power=PowerTelemetry(
            battery_kwh=90.0,
            battery_percent=90.0,
            power_consumption_kw=5.0,
            estimated_power_remaining_h=18.0,
        ),
    )


async def test_connected_client_receives_telemetry() -> None:
    manager = WebSocketManager()
    websocket = FakeWebSocket()
    telemetry = _telemetry()

    await manager.connect(
        telemetry.mission_id,
        websocket,  # type: ignore[arg-type]
    )

    await manager.broadcast_telemetry(telemetry)

    assert websocket.accepted
    assert len(websocket.messages) == 1

    assert websocket.messages[0]["type"] == "telemetry"
