from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.domain.enums import MissionEventType
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.mission import Mission


json_type = JSON().with_variant(JSONB(), "postgresql")


class MissionEvent(Base):
    __tablename__ = "mission_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    mission_id: Mapped[UUID] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[MissionEventType] = mapped_column(
        Enum(MissionEventType, name="mission_event_type"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(json_type, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True
    )

    mission: Mapped["Mission"] = relationship(back_populates="events")
