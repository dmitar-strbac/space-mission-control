import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s", settings.service_name)

    yield

    logger.info("Stopping %s", settings.service_name)


app = FastAPI(
    title=settings.service_title,
    description="Part of the Space Mission Control platform.",
    version=settings.service_version,
    lifespan=lifespan,
)

app.include_router(health_router)


@app.get("/", tags=["Root"])
def get_root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "message": f"{settings.service_title} is running.",
        "documentation": "/docs",
    }
