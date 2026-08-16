from functools import lru_cache
from typing import Literal

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

    jwt_secret_key: str = "development-only-secret-change-me"
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = 60

    operator_username: str = "operator"
    operator_password_hash: str = (
        "$argon2id$v=19$m=65536,t=3,p=4$"
        "dc7nrPgaJQF4U+0AQcFo+w$"
        "eFCuhrzoPez2+h32Fy7z9eo0t9aypgyFjjvi+wCucVY"
    )

    observer_username: str = "observer"
    observer_password_hash: str = (
        "$argon2id$v=19$m=65536,t=3,p=4$"
        "/CILjrqt1svO60GqYfaNxQ$"
        "VnGezC+uJ8zDrJsFz2+5nc4nodvTqRt+OG1ZoAL4C38"
    )

    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
