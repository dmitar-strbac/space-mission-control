import asyncio
from typing import TypedDict

import httpx
from fastapi import APIRouter, Request

from app.clients.registry import (
    ServiceRegistry,
    ServiceTarget,
)
from app.core.config import get_settings


class HealthResponse(TypedDict):
    status: str
    service: str
    version: str
    environment: str


class DownstreamHealth(TypedDict):
    status: str
    circuit_state: str


class ServicesHealthResponse(TypedDict):
    status: str
    services: dict[str, DownstreamHealth]


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
)
def get_health() -> HealthResponse:
    settings = get_settings()

    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
    }


async def _probe_service(
    client: httpx.AsyncClient,
    target: ServiceTarget,
) -> tuple[str, DownstreamHealth]:
    try:
        response = await client.get(f"{target.base_url}/health")
        healthy = response.is_success
    except httpx.RequestError:
        healthy = False

    return (
        target.name,
        {
            "status": ("healthy" if healthy else "unavailable"),
            "circuit_state": (target.circuit_breaker.state.value),
        },
    )


@router.get(
    "/services",
    response_model=ServicesHealthResponse,
)
async def get_services_health(
    request: Request,
) -> ServicesHealthResponse:
    registry: ServiceRegistry = request.app.state.service_registry
    client: httpx.AsyncClient = request.app.state.http_client

    service_results = await asyncio.gather(
        *(
            _probe_service(
                client,
                target,
            )
            for target in registry.values()
        )
    )

    services = dict(service_results)

    overall_status = (
        "healthy"
        if all(service["status"] == "healthy" for service in services.values())
        else "degraded"
    )

    return {
        "status": overall_status,
        "services": services,
    }
