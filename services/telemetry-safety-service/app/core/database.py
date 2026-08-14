from typing import Any

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings

settings = get_settings()

mongo_client: AsyncMongoClient[dict[str, Any]] | None = None


def get_mongo_client() -> AsyncMongoClient[dict[str, Any]]:
    global mongo_client

    if mongo_client is None:
        mongo_client = AsyncMongoClient(settings.mongodb_url)

    return mongo_client


def get_database() -> AsyncDatabase[dict[str, Any]]:
    client = get_mongo_client()

    return client[settings.mongodb_database_name]


async def initialize_database() -> None:
    database = get_database()

    await database.telemetry_points.create_index(
        [
            ("mission_id", 1),
            ("recorded_at", -1),
        ]
    )

    await database.alerts.create_index(
        [
            ("mission_id", 1),
            ("created_at", -1),
        ]
    )

    await database.alerts.create_index(
        [
            ("mission_id", 1),
            ("alert_type", 1),
            ("resolved_at", 1),
        ]
    )

    await database.anomaly_events.create_index(
        [
            ("mission_id", 1),
            ("created_at", -1),
        ]
    )


async def close_database() -> None:
    global mongo_client

    if mongo_client is not None:
        await mongo_client.close()
        mongo_client = None
