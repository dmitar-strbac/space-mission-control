from typing import Any
from uuid import UUID

from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.telemetry import TelemetryPoint


class TelemetryRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self._collection = database.telemetry_points

    async def create(
        self,
        telemetry: TelemetryPoint,
    ) -> None:
        document = telemetry.model_dump()

        document["mission_id"] = str(telemetry.mission_id)
        document["simulation_session_id"] = str(telemetry.simulation_session_id)

        await self._collection.insert_one(document)

    async def get_latest(
        self,
        mission_id: UUID,
    ) -> TelemetryPoint | None:
        document = await self._collection.find_one(
            {
                "mission_id": str(mission_id),
            },
            sort=[
                ("recorded_at", -1),
            ],
        )

        if document is None:
            return None

        document.pop("_id", None)

        return TelemetryPoint.model_validate(document)

    async def list_recent(
        self,
        mission_id: UUID,
        *,
        limit: int,
    ) -> list[TelemetryPoint]:
        cursor = (
            self._collection.find(
                {
                    "mission_id": str(mission_id),
                }
            )
            .sort(
                "recorded_at",
                -1,
            )
            .limit(limit)
        )

        documents = await cursor.to_list(length=limit)

        telemetry_points: list[TelemetryPoint] = []

        for document in reversed(documents):
            document.pop("_id", None)

            telemetry_points.append(TelemetryPoint.model_validate(document))

        return telemetry_points
