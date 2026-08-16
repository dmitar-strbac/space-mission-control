from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "api-gateway"
    service_title: str = "API Gateway"
    service_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    mission_service_url: str = "http://mission-service:8001"
    vehicle_service_url: str = "http://vehicle-service:8002"
    trajectory_service_url: str = "http://trajectory-service:8003"
    flight_dynamics_service_url: str = "http://flight-dynamics-service:8004"
    communication_service_url: str = "http://communication-service:8005"
    telemetry_service_url: str = "http://telemetry-safety-service:8006"

    request_timeout_seconds: float = 5.0
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_recovery_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
