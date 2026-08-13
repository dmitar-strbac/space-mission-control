from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import JSON

from app.domain.enums import (
    SagaStepStatus,
    SagaStepType,
)
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.mission import Mission


json_type = JSON().with_variant(
    JSONB(),
    "postgresql",
)


class SagaStep(Base):
    __tablename__ = "saga_steps"

    __table_args__ = (
        UniqueConstraint(
            "saga_id",
            "step_type",
            name="uq_saga_steps_saga_step",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    saga_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    mission_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "missions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    step_type: Mapped[SagaStepType] = mapped_column(
        Enum(
            SagaStepType,
            name="saga_step_type",
        ),
        nullable=False,
    )

    status: Mapped[SagaStepStatus] = mapped_column(
        Enum(
            SagaStepStatus,
            name="saga_step_status",
        ),
        nullable=False,
        default=SagaStepStatus.PENDING,
        index=True,
    )

    request_event_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    result_event_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    request_payload: Mapped[dict[str, Any] | None] = mapped_column(
        json_type,
        nullable=True,
    )

    result_payload: Mapped[dict[str, Any] | None] = mapped_column(
        json_type,
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    compensated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    mission: Mapped["Mission"] = relationship(
        back_populates="saga_steps",
    )
