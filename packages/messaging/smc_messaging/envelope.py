from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str = Field(min_length=1)

    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    correlation_id: str = Field(min_length=1)
    causation_id: str | None = None

    schema_version: int = Field(
        default=1,
        ge=1,
    )

    source: str = Field(min_length=1)

    payload: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        event_type: str,
        source: str,
        correlation_id: str,
        payload: dict[str, Any],
        causation_id: UUID | str | None = None,
    ) -> "EventEnvelope":
        return cls(
            event_type=event_type,
            source=source,
            correlation_id=correlation_id,
            causation_id=(str(causation_id) if causation_id is not None else None),
            payload=payload,
        )

    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
    ) -> "EventEnvelope":
        return cls.model_validate_json(data.decode("utf-8"))
