from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import SignalStatus
from app.models.base import Base


class CommunicationProfile(Base):
    __tablename__ = "communication_profiles"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    mission_id: Mapped[UUID] = mapped_column(
        nullable=False,
        unique=True,
        index=True,
    )

    distance_m: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    additional_latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    packet_loss_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    signal_status: Mapped[SignalStatus] = mapped_column(
        Enum(
            SignalStatus,
            name="communication_signal_status",
        ),
        nullable=False,
        default=SignalStatus.AVAILABLE,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
