import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.routes.health import router as health_router
from app.api.routes.proxy import router as proxy_router
from app.api.routes.websocket import router as websocket_router
from app.clients.registry import build_service_registry
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    logger.info(
        "Starting %s",
        settings.service_name,
    )

    app.state.http_client = httpx.AsyncClient(
        timeout=settings.request_timeout_seconds,
    )

    app.state.service_registry = build_service_registry(settings)

    yield

    await app.state.http_client.aclose()

    logger.info(
        "Stopping %s",
        settings.service_name,
    )


app = FastAPI(
    title=settings.service_title,
    description=("Part of the Space Mission Control platform."),
    version=settings.service_version,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(proxy_router)
app.include_router(websocket_router)


@app.get("/", tags=["Root"])
def get_root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "message": (f"{settings.service_title} is running."),
        "documentation": "/docs",
    }
