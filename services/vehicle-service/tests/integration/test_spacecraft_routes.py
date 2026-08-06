from typing import Any

import pytest
from httpx import AsyncClient


def spacecraft_payload(
    *,
    name: str = "Odyssey",
    status: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "vehicle_type": "ORBITAL_VEHICLE",
        "supported_mission_types": [
            "LEO",
            "LEO_RENDEZVOUS",
        ],
        "dry_mass_kg": 8_000.0,
        "max_payload_kg": 2_000.0,
        "crew_capacity": 4,
        "engine_thrust_n": 450_000.0,
        "engine_specific_impulse_s": 320.0,
        "propellant_capacity_kg": 4_000.0,
        "oxygen_capacity_kg": 120.0,
        "battery_capacity_kwh": 500.0,
        "max_mission_duration_h": 72.0,
        "max_acceleration_g": 4.0,
    }

    if status is not None:
        payload["status"] = status

    return payload


@pytest.mark.asyncio
async def test_create_and_get_spacecraft(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/spacecraft",
        json=spacecraft_payload(),
    )

    assert create_response.status_code == 201

    created = create_response.json()
    spacecraft_id = created["id"]

    assert created["name"] == "Odyssey"
    assert created["status"] == "AVAILABLE"
    assert created["fully_fueled_mass_kg"] == pytest.approx(12_000.0)

    get_response = await client.get(f"/spacecraft/{spacecraft_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == spacecraft_id


@pytest.mark.asyncio
async def test_list_spacecraft_is_paginated(
    client: AsyncClient,
) -> None:
    await client.post(
        "/spacecraft",
        json=spacecraft_payload(name="Odyssey"),
    )
    await client.post(
        "/spacecraft",
        json=spacecraft_payload(name="Endeavour"),
    )

    response = await client.get(
        "/spacecraft",
        params={
            "offset": 0,
            "limit": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 2
    assert body["offset"] == 0
    assert body["limit"] == 1
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_duplicate_name_returns_conflict(
    client: AsyncClient,
) -> None:
    await client.post(
        "/spacecraft",
        json=spacecraft_payload(name="Odyssey"),
    )

    response = await client.post(
        "/spacecraft",
        json=spacecraft_payload(name="odyssey"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == ("SPACECRAFT_NAME_CONFLICT")


@pytest.mark.asyncio
async def test_update_spacecraft(
    client: AsyncClient,
) -> None:
    created = (
        await client.post(
            "/spacecraft",
            json=spacecraft_payload(),
        )
    ).json()

    update_payload = spacecraft_payload(
        name="Odyssey II",
        status="MAINTENANCE",
    )

    response = await client.put(
        f"/spacecraft/{created['id']}",
        json=update_payload,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Odyssey II"
    assert response.json()["status"] == "MAINTENANCE"


@pytest.mark.asyncio
async def test_reserved_status_cannot_be_assigned_manually(
    client: AsyncClient,
) -> None:
    created = (
        await client.post(
            "/spacecraft",
            json=spacecraft_payload(),
        )
    ).json()

    response = await client.put(
        f"/spacecraft/{created['id']}",
        json=spacecraft_payload(status="RESERVED"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == ("INVALID_MANUAL_SPACECRAFT_STATUS")


@pytest.mark.asyncio
async def test_preliminary_validation_returns_delta_v(
    client: AsyncClient,
) -> None:
    created = (
        await client.post(
            "/spacecraft",
            json=spacecraft_payload(),
        )
    ).json()

    response = await client.post(
        f"/spacecraft/{created['id']}/validate",
        json={
            "mission_type": "LEO",
            "crew_count": 3,
            "payload_mass_kg": 1_000.0,
            "estimated_duration_h": 24.0,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["valid"] is True
    assert body["initial_mass_kg"] == pytest.approx(13_000.0)
    assert body["available_delta_v_m_s"] > 0.0
    assert body["violations"] == []


@pytest.mark.asyncio
async def test_validation_returns_all_violations(
    client: AsyncClient,
) -> None:
    created = (
        await client.post(
            "/spacecraft",
            json=spacecraft_payload(),
        )
    ).json()

    maintenance_payload = spacecraft_payload(
        status="MAINTENANCE",
    )

    await client.put(
        f"/spacecraft/{created['id']}",
        json=maintenance_payload,
    )

    response = await client.post(
        f"/spacecraft/{created['id']}/validate",
        json={
            "mission_type": "LUNAR",
            "crew_count": 8,
            "payload_mass_kg": 5_000.0,
            "estimated_duration_h": 200.0,
        },
    )

    assert response.status_code == 200

    body = response.json()
    codes = {violation["code"] for violation in body["violations"]}

    assert body["valid"] is False
    assert codes == {
        "VEHICLE_NOT_AVAILABLE",
        "MISSION_TYPE_NOT_SUPPORTED",
        "CREW_CAPACITY_EXCEEDED",
        "PAYLOAD_CAPACITY_EXCEEDED",
        "MISSION_DURATION_EXCEEDED",
    }


@pytest.mark.asyncio
async def test_delete_spacecraft(
    client: AsyncClient,
) -> None:
    created = (
        await client.post(
            "/spacecraft",
            json=spacecraft_payload(),
        )
    ).json()

    response = await client.delete(f"/spacecraft/{created['id']}")

    assert response.status_code == 204

    get_response = await client.get(f"/spacecraft/{created['id']}")

    assert get_response.status_code == 404
