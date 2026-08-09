from enum import StrEnum


class ReferenceFrame(StrEnum):
    EARTH_CENTERED_INERTIAL = "EARTH_CENTERED_INERTIAL"


class ManeuverType(StrEnum):
    ORBIT_INSERTION = "ORBIT_INSERTION"
    ORBIT_RAISE = "ORBIT_RAISE"
    ORBIT_LOWER = "ORBIT_LOWER"
    MIDCOURSE_CORRECTION = "MIDCOURSE_CORRECTION"
    DEORBIT_BURN = "DEORBIT_BURN"


class TrajectoryStatus(StrEnum):
    PLANNED = "PLANNED"
    INFEASIBLE = "INFEASIBLE"
    SUPERSEDED = "SUPERSEDED"


class ManeuverStatus(StrEnum):
    PLANNED = "PLANNED"
    CANCELLED = "CANCELLED"


class LaunchWindowStatus(StrEnum):
    VALID = "VALID"
    VALID_WITH_RISK = "VALID_WITH_RISK"
    INVALID = "INVALID"
