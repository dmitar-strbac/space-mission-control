from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "telemetry-safety-service"
    service_title: str = "Telemetry & Safety Service"
    service_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    nats_url: str = "nats://nats:4222"
    messaging_enabled: bool = False

    database_url: str = Field(
        default=("mongodb://space_admin:space_admin@mongodb:27017/telemetry_db?authSource=admin")
    )
    database_name: str = "telemetry_db"

    propellant_low_percent: float = 20.0
    propellant_critical_percent: float = 10.0

    oxygen_low_percent: float = 20.0
    oxygen_critical_percent: float = 10.0

    battery_low_percent: float = 20.0
    battery_critical_percent: float = 10.0

    trajectory_deviation_warning_km: float = 5.0
    trajectory_deviation_critical_km: float = 20.0

    communication_packet_loss_warning_percent: float = 20.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
