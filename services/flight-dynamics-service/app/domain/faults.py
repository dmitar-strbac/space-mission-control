from dataclasses import dataclass
from enum import StrEnum


class FaultType(StrEnum):
    ENGINE_FAILURE = "ENGINE_FAILURE"
    PROPELLANT_LEAK = "PROPELLANT_LEAK"
    OXYGEN_LEAK = "OXYGEN_LEAK"
    POWER_FAILURE = "POWER_FAILURE"
    TARGETING_ERROR = "TARGETING_ERROR"


@dataclass(frozen=True, slots=True)
class ActiveFault:
    fault_type: FaultType
    magnitude: float
