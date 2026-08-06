from dataclasses import dataclass

from app.domain.enums import (
    MissionType,
    SpacecraftStatus,
    ValidationViolationCode,
)
from orbital_mechanics import available_delta_v_m_s


@dataclass(frozen=True, slots=True)
class ValidationViolationData:
    code: ValidationViolationCode
    message: str


@dataclass(frozen=True, slots=True)
class PreliminaryValidationResult:
    valid: bool
    initial_mass_kg: float
    available_delta_v_m_s: float
    violations: tuple[ValidationViolationData, ...]


def validate_preliminary_configuration(
    *,
    status: SpacecraftStatus,
    supported_mission_types: frozenset[MissionType],
    requested_mission_type: MissionType,
    crew_capacity: int,
    requested_crew_count: int,
    max_payload_kg: float,
    requested_payload_mass_kg: float,
    max_mission_duration_h: float,
    requested_duration_h: float,
    dry_mass_kg: float,
    propellant_capacity_kg: float,
    engine_specific_impulse_s: float,
) -> PreliminaryValidationResult:
    violations: list[ValidationViolationData] = []

    if status is not SpacecraftStatus.AVAILABLE:
        violations.append(
            ValidationViolationData(
                code=ValidationViolationCode.VEHICLE_NOT_AVAILABLE,
                message=(
                    f"Spacecraft is not available for mission preparation. "
                    f"Current status: {status.value}."
                ),
            )
        )

    if requested_mission_type not in supported_mission_types:
        violations.append(
            ValidationViolationData(
                code=ValidationViolationCode.MISSION_TYPE_NOT_SUPPORTED,
                message=(
                    f"Spacecraft does not support mission type '{requested_mission_type.value}'."
                ),
            )
        )

    if requested_crew_count > crew_capacity:
        violations.append(
            ValidationViolationData(
                code=ValidationViolationCode.CREW_CAPACITY_EXCEEDED,
                message=(
                    f"Requested crew count of {requested_crew_count} exceeds "
                    f"the spacecraft capacity of {crew_capacity}."
                ),
            )
        )

    if requested_payload_mass_kg > max_payload_kg:
        violations.append(
            ValidationViolationData(
                code=ValidationViolationCode.PAYLOAD_CAPACITY_EXCEEDED,
                message=(
                    f"Requested payload mass of {requested_payload_mass_kg:.2f} kg "
                    f"exceeds the maximum payload of {max_payload_kg:.2f} kg."
                ),
            )
        )

    if requested_duration_h > max_mission_duration_h:
        violations.append(
            ValidationViolationData(
                code=ValidationViolationCode.MISSION_DURATION_EXCEEDED,
                message=(
                    f"Estimated mission duration of {requested_duration_h:.2f} hours "
                    f"exceeds the maximum duration of "
                    f"{max_mission_duration_h:.2f} hours."
                ),
            )
        )

    initial_mass_kg = dry_mass_kg + requested_payload_mass_kg + propellant_capacity_kg

    delta_v_m_s = available_delta_v_m_s(
        total_mass_kg=initial_mass_kg,
        propellant_mass_kg=propellant_capacity_kg,
        specific_impulse_s=engine_specific_impulse_s,
    )

    return PreliminaryValidationResult(
        valid=not violations,
        initial_mass_kg=initial_mass_kg,
        available_delta_v_m_s=delta_v_m_s,
        violations=tuple(violations),
    )
