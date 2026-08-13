from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    event_id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
