from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "trajectory-service"
    service_title: str = "Trajectory Service"
    service_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    nats_url: str = "nats://nats:4222"
    database_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
