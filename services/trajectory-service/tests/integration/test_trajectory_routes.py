from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient


def _valid_request(
    mission_id: str,
) -> dict[str, object]:
    return {
        "mission_id": mission_id,
        "initial_altitude_m": 400000.0,
        "target_altitude_m": 600000.0,
        "total_mass_kg": 20000.0,
        "available_propellant_kg": 8000.0,
        "engine_specific_impulse_s": 450.0,
        "departure_time": datetime.now(UTC).isoformat(),
        "minimum_propellant_reserve_percent": 10.0,
    }


def test_plan_trajectory(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    response = client.post(
        "/trajectories/plan",
        json=_valid_request(mission_id),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["mission_id"] == mission_id
    assert body["status"] == "PLANNED"
    assert body["required_delta_v_m_s"] > 0
    assert body["estimated_propellant_kg"] > 0
    assert body["window_score"] > 0
    assert len(body["maneuvers"]) == 2


def test_get_trajectory_after_planning(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    create_response = client.post(
        "/trajectories/plan",
        json=_valid_request(mission_id),
    )

    assert create_response.status_code == 201

    response = client.get(f"/trajectories/{mission_id}")

    assert response.status_code == 200
    assert response.json()["mission_id"] == mission_id


def test_get_maneuvers(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    client.post(
        "/trajectories/plan",
        json=_valid_request(mission_id),
    )

    response = client.get(f"/trajectories/{mission_id}/maneuvers")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["sequence"] == 1
    assert body[1]["sequence"] == 2
    assert body[0]["maneuver_type"] == "ORBIT_RAISE"


def test_get_unknown_trajectory_returns_404(
    client: TestClient,
) -> None:
    mission_id = uuid4()

    response = client.get(f"/trajectories/{mission_id}")

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == ("TRAJECTORY_PLAN_NOT_FOUND")


def test_plan_rejects_propellant_greater_than_total_mass(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    payload = _valid_request(mission_id)
    payload["total_mass_kg"] = 1000.0
    payload["available_propellant_kg"] = 2000.0

    response = client.post(
        "/trajectories/plan",
        json=payload,
    )

    assert response.status_code == 422


def test_plan_rejects_departure_time_without_timezone(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    payload = _valid_request(mission_id)
    payload["departure_time"] = "2026-08-09T12:00:00"

    response = client.post(
        "/trajectories/plan",
        json=payload,
    )

    assert response.status_code == 422
