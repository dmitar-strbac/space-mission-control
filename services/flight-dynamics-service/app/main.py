import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.routes.faults import router as faults_router
from app.api.routes.health import router as health_router
from app.api.routes.simulations import router as simulations_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.logging import configure_logging
from app.messaging.publisher import event_bus
from app.messaging.saga_worker import register_flight_dynamics_saga_worker
from app.services.runtime_store import runtime_store

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

    if settings.messaging_enabled:
        await event_bus.connect()

        await register_flight_dynamics_saga_worker(event_bus)

    yield

    if settings.messaging_enabled:
        await event_bus.close()

    runtime_store.clear()

    await engine.dispose()

    logger.info(
        "Stopping %s",
        settings.service_name,
    )


app = FastAPI(
    title=settings.service_title,
    description=(
        "Orbital flight dynamics and simulation execution service for Space Mission Control."
    ),
    version=settings.service_version,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(simulations_router)
app.include_router(faults_router)


@app.get("/", tags=["Root"])
def get_root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "message": (f"{settings.service_title} is running."),
        "documentation": "/docs",
    }
