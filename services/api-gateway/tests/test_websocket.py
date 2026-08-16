from collections.abc import AsyncIterator
from types import TracebackType

from fastapi.testclient import TestClient

from app.auth.models import (
    AuthenticatedUser,
    UserRole,
)
from app.auth.security import create_access_token
from app.main import app


class FakeDownstreamWebSocket:
    def __init__(self) -> None:
        self._messages = iter([('{"type":"telemetry","altitude_km":400.0}')])

    async def send(
        self,
        message: str | bytes,
    ) -> None:
        return None

    def __aiter__(
        self,
    ) -> AsyncIterator[str | bytes]:
        return self

    async def __anext__(
        self,
    ) -> str | bytes:
        try:
            return next(self._messages)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class FakeConnection:
    def __init__(
        self,
        downstream: FakeDownstreamWebSocket,
    ) -> None:
        self._downstream = downstream

    async def __aenter__(
        self,
    ) -> FakeDownstreamWebSocket:
        return self._downstream

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None


def test_websocket_proxy_forwards_telemetry(
    monkeypatch,
) -> None:
    downstream = FakeDownstreamWebSocket()
    captured_url: list[str] = []

    def fake_connect(
        url: str,
    ) -> FakeConnection:
        captured_url.append(url)

        return FakeConnection(downstream)

    monkeypatch.setattr(
        "app.api.routes.websocket.connect",
        fake_connect,
    )

    token = create_access_token(
        AuthenticatedUser(
            username="observer",
            role=UserRole.OBSERVER,
        )
    )

    with TestClient(app) as client:
        with client.websocket_connect(
            f"/ws/missions/mission-1/telemetry?token={token}"
        ) as websocket:
            message = websocket.receive_text()

    assert message == ('{"type":"telemetry","altitude_km":400.0}')

    assert captured_url == [("ws://telemetry-safety-service:8006/ws/missions/mission-1/telemetry")]
