from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "flight-dynamics-service",
        "version": "0.1.0",
        "environment": "development",
    }


def test_root_endpoint_returns_service_information() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "flight-dynamics-service",
        "message": "Flight Dynamics Service is running.",
        "documentation": "/docs",
    }
