from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.domain.enums import MissionPhase, MissionStatus, MissionType
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.mission_event import MissionEvent
    from app.models.saga_step import SagaStep

json_type = JSON().with_variant(JSONB(), "postgresql")


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    mission_type: Mapped[MissionType] = mapped_column(
        Enum(MissionType, name="mission_type"), nullable=False
    )
    status: Mapped[MissionStatus] = mapped_column(
        Enum(MissionStatus, name="mission_status"),
        nullable=False,
        default=MissionStatus.DRAFT,
        index=True,
    )
    mission_phase: Mapped[MissionPhase | None] = mapped_column(
        Enum(MissionPhase, name="mission_phase"), nullable=True
    )
    vehicle_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    crew_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_parameters: Mapped[dict[str, Any]] = mapped_column(json_type, nullable=False)
    planned_launch_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    simulation_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(String(500))

    events: Mapped[list["MissionEvent"]] = relationship(
        back_populates="mission",
        cascade="all, delete-orphan",
        order_by="MissionEvent.occurred_at",
    )

    saga_steps: Mapped[list["SagaStep"]] = relationship(
        back_populates="mission",
        cascade="all, delete-orphan",
        order_by="SagaStep.created_at",
    )
