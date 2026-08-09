from fastapi.testclient import TestClient


def test_health_endpoint_returns_service_status(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "flight-dynamics-service",
        "version": "0.2.0",
        "environment": "development",
    }


def test_root_endpoint_returns_service_information(
    client: TestClient,
) -> None:
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "service": "flight-dynamics-service",
        "message": "Flight Dynamics Service is running.",
        "documentation": "/docs",
    }
