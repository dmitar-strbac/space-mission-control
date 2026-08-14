from datetime import datetime
from typing import Any
from uuid import UUID

from pymongo.asynchronous.database import AsyncDatabase

from app.domain.enums import AlertType
from app.schemas.alerts import AlertRecord


class AlertRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self._collection = database.alerts

    async def create(
        self,
        alert: AlertRecord,
    ) -> None:
        document = alert.model_dump()

        document["id"] = str(alert.id)
        document["mission_id"] = str(alert.mission_id)

        await self._collection.insert_one(document)

    async def get_active(
        self,
        *,
        mission_id: UUID,
        alert_type: AlertType,
    ) -> AlertRecord | None:
        document = await self._collection.find_one(
            {
                "mission_id": str(mission_id),
                "alert_type": alert_type.value,
                "resolved_at": None,
            }
        )

        if document is None:
            return None

        document.pop("_id", None)

        return AlertRecord.model_validate(document)

    async def update_active(
        self,
        alert: AlertRecord,
    ) -> None:
        await self._collection.update_one(
            {
                "id": str(alert.id),
            },
            {
                "$set": {
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "measured_value": (alert.measured_value),
                    "threshold": alert.threshold,
                    "last_seen_at": (alert.last_seen_at),
                }
            },
        )

    async def resolve_absent(
        self,
        *,
        mission_id: UUID,
        active_types: set[AlertType],
        resolved_at: datetime,
    ) -> None:
        active_values = [alert_type.value for alert_type in active_types]

        filter_query: dict[str, Any] = {
            "mission_id": str(mission_id),
            "resolved_at": None,
        }

        if active_values:
            filter_query["alert_type"] = {
                "$nin": active_values,
            }

        await self._collection.update_many(
            filter_query,
            {
                "$set": {
                    "resolved_at": resolved_at,
                }
            },
        )

    async def list_by_mission(
        self,
        mission_id: UUID,
        *,
        limit: int,
    ) -> list[AlertRecord]:
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

        alerts: list[AlertRecord] = []

        for document in documents:
            document.pop("_id", None)

            alerts.append(AlertRecord.model_validate(document))

        return alerts
