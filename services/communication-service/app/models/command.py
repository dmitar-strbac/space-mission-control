from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.domain.enums import CommandStatus, CommandType
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.command_log import CommandLog

json_type = JSON().with_variant(JSONB(), "postgresql")


class Command(Base):
    __tablename__ = "commands"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    mission_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    command_type: Mapped[CommandType] = mapped_column(
        Enum(
            CommandType,
            name="command_type",
        ),
        nullable=False,
        index=True,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        json_type,
        nullable=False,
        default=dict,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    scheduled_delivery_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    status: Mapped[CommandStatus] = mapped_column(
        Enum(
            CommandStatus,
            name="command_status",
        ),
        nullable=False,
        default=CommandStatus.CREATED,
        index=True,
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        String(500),
    )

    logs: Mapped[list["CommandLog"]] = relationship(
        back_populates="command",
        cascade="all, delete-orphan",
        order_by="CommandLog.occurred_at",
    )
