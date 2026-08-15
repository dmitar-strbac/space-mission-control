from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.routes.telemetry import get_telemetry_repository
from app.main import app
from app.schemas.telemetry import (
    LifeSupportTelemetry,
    NavigationTelemetry,
    PowerTelemetry,
    PropulsionTelemetry,
    TelemetryPoint,
)


class FakeTelemetryRepository:
    def __init__(
        self,
        telemetry: TelemetryPoint,
    ) -> None:
        self.telemetry = telemetry

    async def get_latest(
        self,
        mission_id: UUID,
    ) -> TelemetryPoint | None:
        if mission_id != self.telemetry.mission_id:
            return None

        return self.telemetry

    async def list_recent(
        self,
        mission_id: UUID,
        *,
        limit: int,
    ) -> list[TelemetryPoint]:
        if mission_id != self.telemetry.mission_id:
            return []

        return [self.telemetry][:limit]


def _telemetry() -> TelemetryPoint:
    return TelemetryPoint(
        mission_id=uuid4(),
        simulation_session_id=uuid4(),
        simulation_time_s=42.0,
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
            remaining_delta_v_m_s=1_500.0,
        ),
        life_support=LifeSupportTelemetry(
            oxygen_kg=95.0,
            oxygen_percent=95.0,
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


def test_get_latest_telemetry() -> None:
    telemetry = _telemetry()

    repository = FakeTelemetryRepository(telemetry)

    app.dependency_overrides[get_telemetry_repository] = lambda: repository

    client = TestClient(app)

    response = client.get(f"/telemetry/{telemetry.mission_id}/latest")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["mission_id"] == str(telemetry.mission_id)
    assert body["navigation"]["altitude_km"] == 400.0


def test_get_recent_telemetry() -> None:
    telemetry = _telemetry()

    repository = FakeTelemetryRepository(telemetry)

    app.dependency_overrides[get_telemetry_repository] = lambda: repository

    client = TestClient(app)

    response = client.get(f"/telemetry/{telemetry.mission_id}?limit=60")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recent_telemetry_limit_is_validated() -> None:
    telemetry = _telemetry()

    repository = FakeTelemetryRepository(telemetry)

    app.dependency_overrides[get_telemetry_repository] = lambda: repository

    client = TestClient(app)

    response = client.get(f"/telemetry/{telemetry.mission_id}?limit=301")

    app.dependency_overrides.clear()

    assert response.status_code == 422
