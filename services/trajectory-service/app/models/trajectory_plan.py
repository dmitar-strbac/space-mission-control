from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.domain.enums import ReferenceFrame, TrajectoryStatus
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.maneuver import Maneuver

json_type = JSON().with_variant(JSONB(), "postgresql")


class TrajectoryPlan(Base):
    __tablename__ = "trajectory_plans"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    mission_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )
    reference_frame: Mapped[ReferenceFrame] = mapped_column(
        Enum(ReferenceFrame, name="trajectory_reference_frame"),
        nullable=False,
        default=ReferenceFrame.EARTH_CENTERED_INERTIAL,
    )

    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    initial_state_vector: Mapped[dict[str, Any]] = mapped_column(
        json_type,
        nullable=False,
    )
    target_state_vector: Mapped[dict[str, Any]] = mapped_column(
        json_type,
        nullable=False,
    )

    required_delta_v_m_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    estimated_propellant_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    propellant_reserve_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    safety_margin_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    window_score: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[TrajectoryStatus] = mapped_column(
        Enum(TrajectoryStatus, name="trajectory_status"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    maneuvers: Mapped[list["Maneuver"]] = relationship(
        back_populates="trajectory_plan",
        cascade="all, delete-orphan",
        order_by="Maneuver.sequence",
    )
