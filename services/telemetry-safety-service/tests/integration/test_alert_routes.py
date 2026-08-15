from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.routes.alerts import (
    get_alert_repository,
    get_anomaly_repository,
)
from app.domain.enums import (
    AlertSeverity,
    AlertType,
)
from app.main import app
from app.schemas.alerts import (
    AlertRecord,
    AnomalyEvent,
)


class FakeAlertRepository:
    def __init__(
        self,
        alert: AlertRecord,
    ) -> None:
        self.alert = alert

    async def list_by_mission(
        self,
        mission_id: UUID,
        *,
        limit: int,
    ) -> list[AlertRecord]:
        if mission_id != self.alert.mission_id:
            return []

        return [self.alert][:limit]


class FakeAnomalyRepository:
    def __init__(
        self,
        anomaly: AnomalyEvent,
    ) -> None:
        self.anomaly = anomaly

    async def list_by_mission(
        self,
        mission_id: UUID,
        *,
        limit: int,
    ) -> list[AnomalyEvent]:
        if mission_id != self.anomaly.mission_id:
            return []

        return [self.anomaly][:limit]


def test_get_mission_alerts() -> None:
    mission_id = uuid4()
    now = datetime.now(UTC)

    alert = AlertRecord(
        mission_id=mission_id,
        alert_type=AlertType.LOW_PROPELLANT,
        severity=AlertSeverity.WARNING,
        message="Propellant is low.",
        measured_value=15.0,
        threshold=20.0,
        created_at=now,
        last_seen_at=now,
    )

    app.dependency_overrides[get_alert_repository] = lambda: FakeAlertRepository(alert)

    client = TestClient(app)

    response = client.get(f"/missions/{mission_id}/alerts")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1

    assert response.json()[0]["alert_type"] == "LOW_PROPELLANT"


def test_get_mission_anomalies() -> None:
    mission_id = uuid4()
    alert_id = uuid4()

    anomaly = AnomalyEvent(
        mission_id=mission_id,
        alert_id=alert_id,
        alert_type=AlertType.LOW_PROPELLANT,
        severity=AlertSeverity.WARNING,
        measured_value=15.0,
        threshold=20.0,
        recommendation=None,
        created_at=datetime.now(UTC),
    )

    app.dependency_overrides[get_anomaly_repository] = lambda: FakeAnomalyRepository(anomaly)

    client = TestClient(app)

    response = client.get(f"/missions/{mission_id}/anomalies")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["alert_id"] == str(alert_id)
