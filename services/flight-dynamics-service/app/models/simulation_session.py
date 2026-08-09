from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.domain.enums import SimulationStatus
from app.models.base import Base

json_type = JSON().with_variant(JSONB(), "postgresql")


class SimulationSession(Base):
    __tablename__ = "simulation_sessions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    mission_id: Mapped[UUID] = mapped_column(
        nullable=False,
        unique=True,
        index=True,
    )
    trajectory_plan_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    status: Mapped[SimulationStatus] = mapped_column(
        Enum(
            SimulationStatus,
            name="simulation_status",
        ),
        nullable=False,
        default=SimulationStatus.INITIALIZED,
        index=True,
    )

    simulation_speed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    integration_step_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    initial_state_vector: Mapped[dict[str, Any]] = mapped_column(
        json_type,
        nullable=False,
    )

    engine_thrust_n: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    engine_specific_impulse_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    oxygen_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    oxygen_consumption_rate_kg_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    battery_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    power_consumption_kw: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    checkpoint_interval_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=60.0,
    )

    planned_maneuvers: Mapped[list[dict[str, Any]]] = mapped_column(
        json_type,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    failure_reason: Mapped[str | None] = mapped_column(
        String(500),
    )
