from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import CommandStatus
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.command import Command


class CommandLog(Base):
    __tablename__ = "command_logs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    command_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "commands.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    previous_status: Mapped[CommandStatus | None] = mapped_column(
        Enum(
            CommandStatus,
            name="command_status",
            create_constraint=False,
        ),
    )

    new_status: Mapped[CommandStatus] = mapped_column(
        Enum(
            CommandStatus,
            name="command_status",
            create_constraint=False,
        ),
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(
        String(500),
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    command: Mapped["Command"] = relationship(
        back_populates="logs",
    )
