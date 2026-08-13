from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "mission-service"
    service_title: str = "Mission Service"
    service_version: str = "0.2.0"
    environment: str = "development"
    log_level: str = "INFO"

    nats_url: str = "nats://nats:4222"
    messaging_enabled: bool = False
    database_url: str = Field(default="postgresql+asyncpg://smc:smc@postgres:5432/mission_service")
    database_echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
