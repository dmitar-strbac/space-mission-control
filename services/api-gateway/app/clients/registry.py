from dataclasses import dataclass

from app.core.config import Settings
from app.resilience.circuit_breaker import CircuitBreaker


@dataclass(frozen=True)
class ServiceTarget:
    name: str
    base_url: str
    circuit_breaker: CircuitBreaker


ServiceRegistry = dict[str, ServiceTarget]


def build_service_registry(settings: Settings) -> ServiceRegistry:
    service_urls = {
        "mission": (
            "mission-service",
            settings.mission_service_url,
        ),
        "vehicle": (
            "vehicle-service",
            settings.vehicle_service_url,
        ),
        "trajectory": (
            "trajectory-service",
            settings.trajectory_service_url,
        ),
        "flight-dynamics": (
            "flight-dynamics-service",
            settings.flight_dynamics_service_url,
        ),
        "communication": (
            "communication-service",
            settings.communication_service_url,
        ),
        "telemetry": (
            "telemetry-safety-service",
            settings.telemetry_service_url,
        ),
    }

    return {
        route_name: ServiceTarget(
            name=service_name,
            base_url=base_url.rstrip("/"),
            circuit_breaker=CircuitBreaker(
                failure_threshold=settings.circuit_breaker_failure_threshold,
                recovery_timeout_seconds=(settings.circuit_breaker_recovery_timeout_seconds),
            ),
        )
        for route_name, (service_name, base_url) in service_urls.items()
    }
