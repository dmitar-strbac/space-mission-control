from dataclasses import dataclass, field
from uuid import UUID

from app.domain.enums import (
    ManeuverExecutionStatus,
    ManeuverType,
)
from orbital_mechanics.models import StateVector, Vector2D


@dataclass(slots=True)
class RuntimeManeuver:
    id: UUID
    sequence: int
    maneuver_type: ManeuverType
    delta_v_m_s: float
    planned_offset_s: float
    direction: Vector2D | None = None

    status: ManeuverExecutionStatus = ManeuverExecutionStatus.PENDING

    remaining_burn_s: float | None = None


@dataclass(slots=True)
class SimulationRuntime:
    state: StateVector

    oxygen_kg: float
    battery_kwh: float

    maneuvers: list[RuntimeManeuver] = field(default_factory=list)

    last_checkpoint_time_s: float = 0.0
