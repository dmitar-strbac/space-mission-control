from uuid import uuid4

from fastapi.testclient import TestClient


def _profile_payload(
    mission_id: str,
    *,
    distance_m: float = 0.0,
    packet_loss_percent: float = 0.0,
    signal_status: str = "AVAILABLE",
) -> dict[str, object]:
    return {
        "mission_id": mission_id,
        "distance_m": distance_m,
        "additional_latency_ms": 0.0,
        "packet_loss_percent": packet_loss_percent,
        "signal_status": signal_status,
    }


def _command_payload(
    mission_id: str,
) -> dict[str, object]:
    return {
        "mission_id": mission_id,
        "command_type": "PAUSE_SIMULATION",
        "payload": {},
    }


def test_create_and_get_communication_profile(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    create_response = client.post(
        "/communication-profiles",
        json=_profile_payload(
            mission_id,
            distance_m=400_000.0,
        ),
    )

    assert create_response.status_code == 201

    body = create_response.json()

    assert body["mission_id"] == mission_id
    assert body["distance_m"] == 400_000.0
    assert body["signal_status"] == "AVAILABLE"

    get_response = client.get(f"/communication-profiles/{mission_id}")

    assert get_response.status_code == 200
    assert get_response.json()["mission_id"] == mission_id


def test_update_communication_profile(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    client.post(
        "/communication-profiles",
        json=_profile_payload(mission_id),
    )

    response = client.patch(
        f"/communication-profiles/{mission_id}",
        json={
            "packet_loss_percent": 25.0,
            "signal_status": "DEGRADED",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["packet_loss_percent"] == 25.0
    assert body["signal_status"] == "DEGRADED"


def test_duplicate_communication_profile_returns_conflict(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())
    payload = _profile_payload(mission_id)

    first = client.post(
        "/communication-profiles",
        json=payload,
    )

    second = client.post(
        "/communication-profiles",
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409

    assert second.json()["error"]["code"] == "COMMUNICATION_PROFILE_ALREADY_EXISTS"


def test_unknown_communication_profile_returns_404(
    client: TestClient,
) -> None:
    response = client.get(f"/communication-profiles/{uuid4()}")

    assert response.status_code == 404

    assert response.json()["error"]["code"] == "COMMUNICATION_PROFILE_NOT_FOUND"


def test_command_full_delivery_flow(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    profile_response = client.post(
        "/communication-profiles",
        json=_profile_payload(
            mission_id,
            distance_m=0.0,
        ),
    )

    assert profile_response.status_code == 201

    create_response = client.post(
        "/commands",
        json=_command_payload(mission_id),
    )

    assert create_response.status_code == 201

    command_id = create_response.json()["id"]

    assert create_response.json()["status"] == "CREATED"

    queue_response = client.post(f"/commands/{command_id}/queue")

    assert queue_response.status_code == 200
    assert queue_response.json()["status"] == "QUEUED"

    dispatch_response = client.post(f"/commands/{command_id}/dispatch")

    assert dispatch_response.status_code == 200

    dispatch_body = dispatch_response.json()

    assert dispatch_body["command"]["status"] == "IN_TRANSIT"

    assert dispatch_body["one_way_delay_ms"] == 0.0

    deliver_response = client.post(f"/commands/{command_id}/deliver")

    assert deliver_response.status_code == 200
    assert deliver_response.json()["status"] == "DELIVERED"

    execute_response = client.post(f"/commands/{command_id}/execute")

    assert execute_response.status_code == 200
    assert execute_response.json()["status"] == "EXECUTED"

    logs_response = client.get(f"/commands/{command_id}/logs")

    assert logs_response.status_code == 200

    statuses = [log["new_status"] for log in logs_response.json()]

    assert statuses == [
        "CREATED",
        "QUEUED",
        "IN_TRANSIT",
        "DELIVERED",
        "EXECUTED",
    ]


def test_list_mission_commands(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    client.post(
        "/communication-profiles",
        json=_profile_payload(mission_id),
    )

    first = client.post(
        "/commands",
        json=_command_payload(mission_id),
    )

    second = client.post(
        "/commands",
        json={
            "mission_id": mission_id,
            "command_type": "RESUME_SIMULATION",
            "payload": {},
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get(f"/missions/{mission_id}/commands")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_command_without_profile_returns_404(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    response = client.post(
        "/commands",
        json=_command_payload(mission_id),
    )

    assert response.status_code == 404

    assert response.json()["error"]["code"] == "COMMUNICATION_PROFILE_NOT_FOUND"


def test_invalid_command_transition_returns_conflict(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    client.post(
        "/communication-profiles",
        json=_profile_payload(mission_id),
    )

    create_response = client.post(
        "/commands",
        json=_command_payload(mission_id),
    )

    command_id = create_response.json()["id"]

    response = client.post(f"/commands/{command_id}/execute")

    assert response.status_code == 409

    assert response.json()["error"]["code"] == "INVALID_COMMAND_TRANSITION"


def test_signal_loss_marks_command_as_lost(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    client.post(
        "/communication-profiles",
        json=_profile_payload(
            mission_id,
            signal_status="LOST",
        ),
    )

    create_response = client.post(
        "/commands",
        json=_command_payload(mission_id),
    )

    command_id = create_response.json()["id"]

    client.post(f"/commands/{command_id}/queue")

    dispatch_response = client.post(f"/commands/{command_id}/dispatch")

    assert dispatch_response.status_code == 409

    assert dispatch_response.json()["error"]["code"] == "COMMAND_DELIVERY_ERROR"

    command_response = client.get(f"/commands/{command_id}")

    assert command_response.status_code == 200
    assert command_response.json()["status"] == "LOST"


def test_reject_command(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    client.post(
        "/communication-profiles",
        json=_profile_payload(mission_id),
    )

    create_response = client.post(
        "/commands",
        json=_command_payload(mission_id),
    )

    command_id = create_response.json()["id"]

    response = client.post(
        f"/commands/{command_id}/reject",
        json={"reason": "Command payload is invalid."},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "REJECTED"
    assert body["rejection_reason"] == "Command payload is invalid."


def test_invalid_profile_values_return_422(
    client: TestClient,
) -> None:
    response = client.post(
        "/communication-profiles",
        json=_profile_payload(
            str(uuid4()),
            packet_loss_percent=101.0,
        ),
    )

    assert response.status_code == 422


def test_inject_and_clear_communication_loss(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    create_response = client.post(
        "/communication-profiles",
        json=_profile_payload(
            mission_id,
            signal_status="AVAILABLE",
        ),
    )

    assert create_response.status_code == 201

    inject_response = client.post(
        "/faults/communication-loss",
        json={
            "mission_id": mission_id,
        },
    )

    assert inject_response.status_code == 200

    inject_body = inject_response.json()

    assert inject_body["mission_id"] == mission_id
    assert inject_body["signal_status"] == "LOST"

    profile_response = client.get(f"/communication-profiles/{mission_id}")

    assert profile_response.status_code == 200

    assert profile_response.json()["signal_status"] == "LOST"

    clear_response = client.delete(f"/faults/communication-loss/{mission_id}")

    assert clear_response.status_code == 200

    clear_body = clear_response.json()

    assert clear_body["mission_id"] == mission_id
    assert clear_body["signal_status"] == "AVAILABLE"


def test_communication_fault_for_unknown_mission_returns_404(
    client: TestClient,
) -> None:
    mission_id = str(uuid4())

    response = client.post(
        "/faults/communication-loss",
        json={
            "mission_id": mission_id,
        },
    )

    assert response.status_code == 404

    assert response.json()["error"]["code"] == "COMMUNICATION_PROFILE_NOT_FOUND"
