import asyncio

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from websockets import connect
from websockets.exceptions import WebSocketException

from app.clients.registry import ServiceRegistry

router = APIRouter(tags=["Telemetry"])


def _to_websocket_url(
    http_url: str,
) -> str:
    if http_url.startswith("https://"):
        return f"wss://{http_url.removeprefix('https://')}"

    if http_url.startswith("http://"):
        return f"ws://{http_url.removeprefix('http://')}"

    raise ValueError(f"Unsupported downstream URL scheme: {http_url}")


@router.websocket("/ws/missions/{mission_id}/telemetry")
async def telemetry_websocket_proxy(
    websocket: WebSocket,
    mission_id: str,
) -> None:
    registry: ServiceRegistry = websocket.app.state.service_registry

    target = registry["telemetry"]

    downstream_url = f"{_to_websocket_url(target.base_url)}/ws/missions/{mission_id}/telemetry"

    try:
        async with connect(downstream_url) as downstream:
            await websocket.accept()

            async def client_to_downstream() -> None:
                while True:
                    message = await websocket.receive()

                    if message["type"] == "websocket.disconnect":
                        return

                    if text := message.get("text"):
                        await downstream.send(text)
                    elif binary := message.get("bytes"):
                        await downstream.send(binary)

            async def downstream_to_client() -> None:
                async for message in downstream:
                    if isinstance(message, str):
                        await websocket.send_text(message)
                    else:
                        await websocket.send_bytes(bytes(message))

            tasks = {
                asyncio.create_task(client_to_downstream()),
                asyncio.create_task(downstream_to_client()),
            }

            _, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            await asyncio.gather(
                *pending,
                return_exceptions=True,
            )

    except WebSocketDisconnect:
        return
    except (OSError, WebSocketException):
        await websocket.close(
            code=1013,
            reason="Telemetry service unavailable",
        )
