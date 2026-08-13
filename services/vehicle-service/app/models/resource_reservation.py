from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ResourceReservation(Base):
    __tablename__ = "resource_reservations"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    mission_id: Mapped[UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        index=True,
    )

    spacecraft_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "spacecraft.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
