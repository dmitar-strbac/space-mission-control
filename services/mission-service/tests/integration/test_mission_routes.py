from uuid import uuid4

from fastapi.testclient import TestClient


def mission_payload() -> dict[str, object]:
    return {
        "name": "LEO Demonstration Mission",
        "mission_type": "LEO",
        "vehicle_id": str(uuid4()),
        "crew_count": 3,
        "target_type": "EARTH_ORBIT",
        "target_parameters": {"altitude_km": 400},
        "planned_launch_time": "2026-08-10T12:00:00+00:00",
        "simulation_speed": 60,
    }


def test_create_get_list_and_timeline(client: TestClient) -> None:
    create_response = client.post("/missions", json=mission_payload())
    assert create_response.status_code == 201
    mission = create_response.json()
    assert mission["status"] == "DRAFT"
    assert mission["mission_phase"] is None

    get_response = client.get(f"/missions/{mission['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "LEO Demonstration Mission"

    list_response = client.get("/missions")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    timeline_response = client.get(f"/missions/{mission['id']}/timeline")
    assert timeline_response.status_code == 200
    assert [event["event_type"] for event in timeline_response.json()] == ["MISSION_CREATED"]


def test_prepare_updates_status_and_timeline(client: TestClient) -> None:
    mission_id = client.post("/missions", json=mission_payload()).json()["id"]
    response = client.post(f"/missions/{mission_id}/prepare")
    assert response.status_code == 200
    assert response.json()["status"] == "PREPARING"

    timeline = client.get(f"/missions/{mission_id}/timeline").json()
    assert [event["event_type"] for event in timeline] == [
        "MISSION_CREATED",
        "PREPARATION_REQUESTED",
    ]


def test_repeated_prepare_returns_conflict(client: TestClient) -> None:
    mission_id = client.post("/missions", json=mission_payload()).json()["id"]
    assert client.post(f"/missions/{mission_id}/prepare").status_code == 200
    response = client.post(f"/missions/{mission_id}/prepare")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_MISSION_TRANSITION"


def test_launch_from_draft_returns_conflict(client: TestClient) -> None:
    mission_id = client.post("/missions", json=mission_payload()).json()["id"]
    response = client.post(f"/missions/{mission_id}/launch")
    assert response.status_code == 409


def test_unknown_mission_returns_not_found(client: TestClient) -> None:
    response = client.get(f"/missions/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "MISSION_NOT_FOUND"


def test_rejects_invalid_simulation_speed(client: TestClient) -> None:
    payload = mission_payload()
    payload["simulation_speed"] = 5
    response = client.post("/missions", json=payload)
    assert response.status_code == 422
