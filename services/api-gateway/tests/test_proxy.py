import httpx
from fastapi.testclient import TestClient

from app.clients.service_client import (
    DownstreamServiceTimeoutError,
    DownstreamServiceUnavailableError,
    ServiceClient,
)
from app.main import app


def test_proxy_forwards_request_to_selected_service(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    async def fake_request(
        self: ServiceClient,
        *,
        target,
        method: str,
        path: str,
        headers,
        query_params,
        body: bytes,
    ) -> httpx.Response:
        captured.update(
            {
                "service": target.name,
                "method": method,
                "path": path,
                "query_params": query_params,
                "body": body,
            }
        )

        return httpx.Response(
            200,
            request=httpx.Request(
                method,
                "http://downstream.test",
            ),
            json={"proxied": True},
        )

    monkeypatch.setattr(
        ServiceClient,
        "request",
        fake_request,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/mission/missions?source=test",
            json={"name": "LEO Demo"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "proxied": True,
    }

    assert captured["service"] == "mission-service"
    assert captured["method"] == "POST"
    assert captured["path"] == "missions"
    assert captured["query_params"] == httpx.QueryParams([("source", "test")])
    assert captured["body"] == (b'{"name":"LEO Demo"}')


def test_unknown_gateway_route_returns_normalized_error() -> None:
    with TestClient(app) as client:
        response = client.get("/api/unknown/resource")

    assert response.status_code == 404

    assert response.json()["error"]["code"] == "UNKNOWN_GATEWAY_ROUTE"


def test_downstream_timeout_returns_gateway_timeout(
    monkeypatch,
) -> None:
    async def fake_request(
        self: ServiceClient,
        **kwargs,
    ) -> httpx.Response:
        raise DownstreamServiceTimeoutError("mission-service")

    monkeypatch.setattr(
        ServiceClient,
        "request",
        fake_request,
    )

    with TestClient(app) as client:
        response = client.get("/api/mission/missions")

    assert response.status_code == 504

    assert response.json()["error"] == {
        "code": "DOWNSTREAM_TIMEOUT",
        "message": ("mission-service did not respond within the configured timeout."),
        "service": "mission-service",
    }


def test_unavailable_downstream_returns_service_unavailable(
    monkeypatch,
) -> None:
    async def fake_request(
        self: ServiceClient,
        **kwargs,
    ) -> httpx.Response:
        raise DownstreamServiceUnavailableError("vehicle-service")

    monkeypatch.setattr(
        ServiceClient,
        "request",
        fake_request,
    )

    with TestClient(app) as client:
        response = client.get("/api/vehicle/spacecraft")

    assert response.status_code == 503

    assert response.json()["error"]["code"] == "DOWNSTREAM_UNAVAILABLE"
