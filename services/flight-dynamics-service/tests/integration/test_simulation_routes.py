from uuid import uuid4

from fastapi.testclient import TestClient


def _payload(
    *,
    mission_id: str | None = None,
    simulation_speed: int = 1,
) -> dict[str, object]:
    return {
        "mission_id": mission_id or str(uuid4()),
        "trajectory_plan_id": str(uuid4()),
        "vehicle_id": str(uuid4()),
        "initial_state_vector": {
            "position": {
                "x": 6_771_000.0,
                "y": 0.0,
            },
            "velocity": {
                "x": 0.0,
                "y": 7_672.0,
            },
            "total_mass_kg": 10_000.0,
            "propellant_mass_kg": 2_000.0,
            "elapsed_time_s": 0.0,
        },
        "planned_maneuvers": [],
        "engine_thrust_n": 100_000.0,
        "engine_specific_impulse_s": 450.0,
        "oxygen_kg": 5.0,
        "oxygen_consumption_rate_kg_s": 0.001,
        "battery_kwh": 10.0,
        "power_consumption_kw": 1.0,
        "simulation_speed": simulation_speed,
        "integration_step_s": 1.0,
        "checkpoint_interval_s": 60.0,
    }


def test_initialize_simulation(
    client: TestClient,
) -> None:
    payload = _payload()

    response = client.post(
        "/simulations/initialize",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["mission_id"] == payload["mission_id"]
    assert body["status"] == "INITIALIZED"
    assert body["simulation_speed"] == 1


def test_get_initialized_simulation(
    client: TestClient,
) -> None:
    payload = _payload()
    mission_id = payload["mission_id"]

    create_response = client.post(
        "/simulations/initialize",
        json=payload,
    )

    assert create_response.status_code == 201

    response = client.get(f"/simulations/{mission_id}")

    assert response.status_code == 200
    assert response.json()["mission_id"] == mission_id


def test_start_advance_and_read_state(
    client: TestClient,
) -> None:
    payload = _payload(simulation_speed=10)
    mission_id = payload["mission_id"]

    client.post(
        "/simulations/initialize",
        json=payload,
    )

    start_response = client.post(f"/simulations/{mission_id}/start")

    assert start_response.status_code == 200
    assert start_response.json()["status"] == "RUNNING"

    advance_response = client.post(
        f"/simulations/{mission_id}/advance",
        json={"real_duration_s": 1.0},
    )

    assert advance_response.status_code == 200

    body = advance_response.json()

    assert body["simulated_duration_s"] == 10.0
    assert body["state"]["elapsed_time_s"] == 10.0

    state_response = client.get(f"/simulations/{mission_id}/state")

    assert state_response.status_code == 200
    assert state_response.json()["elapsed_time_s"] == 10.0


def test_pause_and_resume(
    client: TestClient,
) -> None:
    payload = _payload()
    mission_id = payload["mission_id"]

    client.post(
        "/simulations/initialize",
        json=payload,
    )

    client.post(f"/simulations/{mission_id}/start")

    pause_response = client.post(f"/simulations/{mission_id}/pause")

    assert pause_response.status_code == 200
    assert pause_response.json()["status"] == "PAUSED"

    resume_response = client.post(f"/simulations/{mission_id}/resume")

    assert resume_response.status_code == 200
    assert resume_response.json()["status"] == "RUNNING"


def test_checkpoint_endpoint_returns_initial_checkpoint(
    client: TestClient,
) -> None:
    payload = _payload()
    mission_id = payload["mission_id"]

    client.post(
        "/simulations/initialize",
        json=payload,
    )

    response = client.get(f"/simulations/{mission_id}/checkpoints")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["reason"] == "INITIALIZED"
    assert body[0]["simulated_time_s"] == 0.0


def test_duplicate_initialization_returns_conflict(
    client: TestClient,
) -> None:
    payload = _payload()

    first = client.post(
        "/simulations/initialize",
        json=payload,
    )

    second = client.post(
        "/simulations/initialize",
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409

    assert second.json()["error"]["code"] == "SIMULATION_ALREADY_EXISTS"


def test_unknown_simulation_returns_404(
    client: TestClient,
) -> None:
    response = client.get(f"/simulations/{uuid4()}")

    assert response.status_code == 404

    assert response.json()["error"]["code"] == "SIMULATION_NOT_FOUND"


def test_pause_before_start_returns_conflict(
    client: TestClient,
) -> None:
    payload = _payload()
    mission_id = payload["mission_id"]

    client.post(
        "/simulations/initialize",
        json=payload,
    )

    response = client.post(f"/simulations/{mission_id}/pause")

    assert response.status_code == 409

    assert response.json()["error"]["code"] == "INVALID_SIMULATION_TRANSITION"


def test_invalid_simulation_speed_returns_422(
    client: TestClient,
) -> None:
    response = client.post(
        "/simulations/initialize",
        json=_payload(simulation_speed=5),
    )

    assert response.status_code == 422


def test_planned_maneuver_is_physically_executed(
    client: TestClient,
) -> None:
    payload = _payload()

    payload["planned_maneuvers"] = [
        {
            "id": str(uuid4()),
            "sequence": 1,
            "maneuver_type": "ORBIT_RAISE",
            "delta_v_m_s": 10.0,
            "planned_offset_s": 0.0,
            "direction": None,
        }
    ]

    mission_id = payload["mission_id"]

    initialize_response = client.post(
        "/simulations/initialize",
        json=payload,
    )

    assert initialize_response.status_code == 201

    client.post(f"/simulations/{mission_id}/start")

    response = client.post(
        f"/simulations/{mission_id}/advance",
        json={"real_duration_s": 2.0},
    )

    assert response.status_code == 200

    state = response.json()["state"]

    assert state["propellant_mass_kg"] < 2_000.0
    assert state["total_mass_kg"] < 10_000.0

    assert state["maneuvers"][0]["status"] == "COMPLETED"
