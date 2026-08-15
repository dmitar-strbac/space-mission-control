from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket

from app.schemas.alerts import AlertRecord
from app.schemas.telemetry import TelemetryPoint


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[
            UUID,
            set[WebSocket],
        ] = defaultdict(set)

    async def connect(
        self,
        mission_id: UUID,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

        self._connections[mission_id].add(websocket)

    def disconnect(
        self,
        mission_id: UUID,
        websocket: WebSocket,
    ) -> None:
        connections = self._connections.get(mission_id)

        if connections is None:
            return

        connections.discard(websocket)

        if not connections:
            self._connections.pop(
                mission_id,
                None,
            )

    async def broadcast_telemetry(
        self,
        telemetry: TelemetryPoint,
    ) -> None:
        await self._broadcast(
            mission_id=telemetry.mission_id,
            payload={
                "type": "telemetry",
                "data": telemetry.model_dump(mode="json"),
            },
        )

    async def broadcast_alert(
        self,
        alert: AlertRecord,
    ) -> None:
        await self._broadcast(
            mission_id=alert.mission_id,
            payload={
                "type": "alert",
                "data": alert.model_dump(mode="json"),
            },
        )

    async def _broadcast(
        self,
        *,
        mission_id: UUID,
        payload: dict[str, object],
    ) -> None:
        connections = list(
            self._connections.get(
                mission_id,
                set(),
            )
        )

        disconnected: list[WebSocket] = []

        for websocket in connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(
                mission_id,
                websocket,
            )


websocket_manager = WebSocketManager()
