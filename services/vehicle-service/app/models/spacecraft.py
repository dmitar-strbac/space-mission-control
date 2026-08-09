from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.domain.enums import MissionType, SpacecraftStatus, VehicleType
from app.models.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Spacecraft(Base):
    __tablename__ = "spacecraft"
    __table_args__ = (
        CheckConstraint(
            "dry_mass_kg > 0",
            name="dry_mass_positive",
        ),
        CheckConstraint(
            "max_payload_kg >= 0",
            name="max_payload_non_negative",
        ),
        CheckConstraint(
            "crew_capacity >= 0",
            name="crew_capacity_non_negative",
        ),
        CheckConstraint(
            "engine_thrust_n > 0",
            name="engine_thrust_positive",
        ),
        CheckConstraint(
            "engine_specific_impulse_s > 0",
            name="specific_impulse_positive",
        ),
        CheckConstraint(
            "propellant_capacity_kg > 0",
            name="propellant_capacity_positive",
        ),
        CheckConstraint(
            "oxygen_capacity_kg >= 0",
            name="oxygen_capacity_non_negative",
        ),
        CheckConstraint(
            "battery_capacity_kwh > 0",
            name="battery_capacity_positive",
        ),
        CheckConstraint(
            "max_mission_duration_h > 0",
            name="mission_duration_positive",
        ),
        CheckConstraint(
            "max_acceleration_g > 0",
            name="max_acceleration_positive",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )

    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(
            VehicleType,
            name="vehicle_type",
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )

    supported_mission_types: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )

    dry_mass_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    max_payload_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    crew_capacity: Mapped[int] = mapped_column(
        Integer,
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

    propellant_capacity_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    oxygen_capacity_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    battery_capacity_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    max_mission_duration_h: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    max_acceleration_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[SpacecraftStatus] = mapped_column(
        Enum(
            SpacecraftStatus,
            name="spacecraft_status",
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=SpacecraftStatus.AVAILABLE,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    @property
    def fully_fueled_mass_kg(self) -> float:
        return self.dry_mass_kg + self.propellant_capacity_kg

    def supports_mission(self, mission_type: MissionType) -> bool:
        return mission_type.value in self.supported_mission_types
