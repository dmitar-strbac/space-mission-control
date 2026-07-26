from typing import TypedDict

from fastapi import APIRouter

from app.core.config import get_settings


class HealthResponse(TypedDict):
    status: str
    service: str
    version: str
    environment: str


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_health() -> HealthResponse:
    settings = get_settings()

    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
    }
