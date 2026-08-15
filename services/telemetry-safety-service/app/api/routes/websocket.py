from uuid import UUID

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from app.services.websocket_manager import websocket_manager

router = APIRouter(
    tags=["Real-time Telemetry"],
)


@router.websocket("/ws/missions/{mission_id}/telemetry")
async def telemetry_websocket(
    websocket: WebSocket,
    mission_id: UUID,
) -> None:
    await websocket_manager.connect(
        mission_id,
        websocket,
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(
            mission_id,
            websocket,
        )
