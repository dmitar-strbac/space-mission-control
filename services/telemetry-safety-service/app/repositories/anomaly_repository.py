from typing import Any
from uuid import UUID

from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.alerts import AnomalyEvent


class AnomalyRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self._collection = database.anomaly_events

    async def create(
        self,
        anomaly: AnomalyEvent,
    ) -> None:
        document = anomaly.model_dump()

        document["id"] = str(anomaly.id)
        document["mission_id"] = str(anomaly.mission_id)
        document["alert_id"] = str(anomaly.alert_id)

        await self._collection.insert_one(document)

    async def list_by_mission(
        self,
        mission_id: UUID,
        *,
        limit: int,
    ) -> list[AnomalyEvent]:
        cursor = (
            self._collection.find(
                {
                    "mission_id": str(mission_id),
                }
            )
            .sort(
                "created_at",
                -1,
            )
            .limit(limit)
        )

        documents = await cursor.to_list(length=limit)

        anomalies: list[AnomalyEvent] = []

        for document in documents:
            document.pop("_id", None)

            anomalies.append(AnomalyEvent.model_validate(document))

        return anomalies
