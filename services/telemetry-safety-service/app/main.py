import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.alerts import router as alerts_router
from app.api.routes.health import router as health_router
from app.api.routes.telemetry import router as telemetry_router
from app.api.routes.websocket import router as websocket_router
from app.core.config import get_settings
from app.core.database import (
    close_database,
    initialize_database,
)
from app.core.logging import configure_logging
from app.messaging.publisher import event_bus
from app.messaging.telemetry_worker import register_telemetry_worker
from app.services.communication_state_store import communication_state_store

settings = get_settings()

configure_logging(settings.log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    _: FastAPI,
) -> AsyncIterator[None]:
    logger.info(
        "Starting %s",
        settings.service_name,
    )

    await initialize_database()

    if settings.messaging_enabled:
        await event_bus.connect()

        await register_telemetry_worker(event_bus)

    yield

    if settings.messaging_enabled:
        await event_bus.close()

    communication_state_store.clear()

    await close_database()

    logger.info(
        "Stopping %s",
        settings.service_name,
    )


app = FastAPI(
    title=settings.service_title,
    description=(
        "Real-time telemetry processing and mission safety "
        "monitoring service for Space Mission Control."
    ),
    version=settings.service_version,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(telemetry_router)
app.include_router(alerts_router)
app.include_router(websocket_router)


@app.get("/", tags=["Root"])
def get_root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "message": (f"{settings.service_title} is running."),
        "documentation": "/docs",
    }
