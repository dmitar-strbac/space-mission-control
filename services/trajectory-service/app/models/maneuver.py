from uuid import UUID, uuid4

from sqlalchemy import Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ManeuverStatus, ManeuverType
from app.models.base import Base


class Maneuver(Base):
    __tablename__ = "maneuvers"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    trajectory_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("trajectory_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    maneuver_type: Mapped[ManeuverType] = mapped_column(
        Enum(ManeuverType, name="maneuver_type"),
        nullable=False,
    )

    delta_v_m_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    planned_offset_s: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[ManeuverStatus] = mapped_column(
        Enum(ManeuverStatus, name="maneuver_status"),
        nullable=False,
        default=ManeuverStatus.PLANNED,
    )

    trajectory_plan = relationship(
        "TrajectoryPlan",
        back_populates="maneuvers",
    )
