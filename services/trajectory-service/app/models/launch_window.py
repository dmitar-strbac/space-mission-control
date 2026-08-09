from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import LaunchWindowStatus
from app.models.base import Base


class LaunchWindow(Base):
    __tablename__ = "launch_windows"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    mission_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    window_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    preferred_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    window_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[LaunchWindowStatus] = mapped_column(
        Enum(LaunchWindowStatus, name="launch_window_status"),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(
        String(500),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
