from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.domain.enums import CheckpointReason
from app.models.base import Base

json_type = JSON().with_variant(JSONB(), "postgresql")


class SimulationCheckpoint(Base):
    __tablename__ = "simulation_checkpoints"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    simulation_session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "simulation_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    simulated_time_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    state_vector: Mapped[dict[str, Any]] = mapped_column(
        json_type,
        nullable=False,
    )

    maneuver_states: Mapped[list[dict[str, Any]]] = mapped_column(
        json_type,
        nullable=False,
        default=list,
    )

    oxygen_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    battery_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    reason: Mapped[CheckpointReason] = mapped_column(
        Enum(
            CheckpointReason,
            name="checkpoint_reason",
        ),
        nullable=False,
        default=CheckpointReason.PERIODIC,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
