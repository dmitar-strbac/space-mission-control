import httpx
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_service_status() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "api-gateway",
        "version": "0.1.0",
        "environment": "development",
    }


def test_root_endpoint_returns_service_information() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "api-gateway",
        "message": "API Gateway is running.",
        "documentation": "/docs",
    }


def test_services_health_reports_healthy_downstream_services(
    monkeypatch,
) -> None:
    async def fake_get(
        url: str,
    ) -> httpx.Response:
        request = httpx.Request(
            "GET",
            url,
        )

        return httpx.Response(
            200,
            request=request,
            json={"status": "healthy"},
        )

    with TestClient(app) as client:
        monkeypatch.setattr(
            app.state.http_client,
            "get",
            fake_get,
        )

        response = client.get("/health/services")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert len(payload["services"]) == 6

    assert all(service["status"] == "healthy" for service in payload["services"].values())
