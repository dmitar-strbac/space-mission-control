from dataclasses import dataclass

from app.domain.enums import (
    MissionType,
    SpacecraftStatus,
    ValidationViolationCode,
)
from orbital_mechanics import available_delta_v_m_s

STANDARD_GRAVITY_M_S2 = 9.80665


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


@dataclass(frozen=True, slots=True)
class FinalResourceValidationResult:
    valid: bool
    required_propellant_kg: float
    available_propellant_kg: float
    required_oxygen_kg: float
    available_oxygen_kg: float
    required_energy_kwh: float
    available_energy_kwh: float
    estimated_acceleration_g: float
    violations: tuple[
        ValidationViolationData,
        ...,
    ]


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


def validate_final_resources(
    *,
    total_mass_kg: float,
    required_propellant_kg: float,
    propellant_capacity_kg: float,
    minimum_propellant_reserve_percent: float,
    mission_duration_s: float,
    oxygen_capacity_kg: float,
    oxygen_consumption_rate_kg_s: float,
    battery_capacity_kwh: float,
    power_consumption_kw: float,
    engine_thrust_n: float,
    max_acceleration_g: float,
) -> FinalResourceValidationResult:
    violations: list[ValidationViolationData] = []

    usable_propellant_kg = propellant_capacity_kg * (
        1.0 - minimum_propellant_reserve_percent / 100.0
    )

    if required_propellant_kg > usable_propellant_kg:
        violations.append(
            ValidationViolationData(
                code=(ValidationViolationCode.INSUFFICIENT_PROPELLANT),
                message=(
                    "Trajectory requires "
                    f"{required_propellant_kg:.2f} kg "
                    "of propellant but only "
                    f"{usable_propellant_kg:.2f} kg "
                    "is available after applying "
                    "the safety reserve."
                ),
            )
        )

    required_oxygen_kg = oxygen_consumption_rate_kg_s * mission_duration_s

    if required_oxygen_kg > oxygen_capacity_kg:
        violations.append(
            ValidationViolationData(
                code=(ValidationViolationCode.INSUFFICIENT_OXYGEN),
                message=(
                    "Mission requires "
                    f"{required_oxygen_kg:.2f} kg "
                    "of oxygen but spacecraft "
                    "capacity is "
                    f"{oxygen_capacity_kg:.2f} kg."
                ),
            )
        )

    mission_duration_h = mission_duration_s / 3600.0

    required_energy_kwh = power_consumption_kw * mission_duration_h

    if required_energy_kwh > battery_capacity_kwh:
        violations.append(
            ValidationViolationData(
                code=(ValidationViolationCode.INSUFFICIENT_ENERGY),
                message=(
                    "Mission requires "
                    f"{required_energy_kwh:.2f} kWh "
                    "but spacecraft battery capacity is "
                    f"{battery_capacity_kwh:.2f} kWh."
                ),
            )
        )

    acceleration_m_s2 = engine_thrust_n / total_mass_kg

    acceleration_g = acceleration_m_s2 / STANDARD_GRAVITY_M_S2

    if acceleration_g > max_acceleration_g:
        violations.append(
            ValidationViolationData(
                code=(ValidationViolationCode.MAX_ACCELERATION_EXCEEDED),
                message=(
                    "Estimated acceleration of "
                    f"{acceleration_g:.3f} g "
                    "exceeds spacecraft limit of "
                    f"{max_acceleration_g:.3f} g."
                ),
            )
        )

    return FinalResourceValidationResult(
        valid=not violations,
        required_propellant_kg=(required_propellant_kg),
        available_propellant_kg=(usable_propellant_kg),
        required_oxygen_kg=(required_oxygen_kg),
        available_oxygen_kg=(oxygen_capacity_kg),
        required_energy_kwh=(required_energy_kwh),
        available_energy_kwh=(battery_capacity_kwh),
        estimated_acceleration_g=(acceleration_g),
        violations=tuple(violations),
    )
