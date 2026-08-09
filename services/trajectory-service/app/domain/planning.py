from dataclasses import dataclass

from app.domain.enums import (
    LaunchWindowStatus,
    ManeuverType,
)
from orbital_mechanics.orbits import (
    hohmann_transfer,
    orbital_radius_from_altitude,
)
from orbital_mechanics.propulsion import (
    available_delta_v_m_s,
    required_propellant_mass_kg,
)


@dataclass(frozen=True, slots=True)
class PlannedManeuverData:
    sequence: int
    maneuver_type: ManeuverType
    delta_v_m_s: float
    planned_offset_s: float


@dataclass(frozen=True, slots=True)
class TrajectoryCalculationResult:
    feasible: bool
    required_delta_v_m_s: float
    available_delta_v_m_s: float
    estimated_propellant_kg: float
    propellant_reserve_percent: float
    safety_margin_percent: float
    estimated_duration_s: float
    window_score: int
    window_status: LaunchWindowStatus
    warnings: tuple[str, ...]
    maneuvers: tuple[PlannedManeuverData, ...]


def calculate_leo_trajectory(
    *,
    initial_altitude_m: float,
    target_altitude_m: float,
    total_mass_kg: float,
    available_propellant_kg: float,
    engine_specific_impulse_s: float,
    minimum_propellant_reserve_percent: float,
) -> TrajectoryCalculationResult:
    initial_radius_m = orbital_radius_from_altitude(initial_altitude_m)
    target_radius_m = orbital_radius_from_altitude(target_altitude_m)

    transfer = hohmann_transfer(
        initial_orbital_radius_m=initial_radius_m,
        target_orbital_radius_m=target_radius_m,
    )

    required_propellant_kg = required_propellant_mass_kg(
        total_mass_kg=total_mass_kg,
        required_delta_v_m_s=transfer.total_delta_v_m_s,
        specific_impulse_s=engine_specific_impulse_s,
    )

    available_delta_v = available_delta_v_m_s(
        total_mass_kg=total_mass_kg,
        propellant_mass_kg=available_propellant_kg,
        specific_impulse_s=engine_specific_impulse_s,
    )

    required_reserve_kg = available_propellant_kg * minimum_propellant_reserve_percent / 100.0

    usable_propellant_kg = max(
        available_propellant_kg - required_reserve_kg,
        0.0,
    )

    feasible = required_propellant_kg <= usable_propellant_kg

    remaining_propellant_kg = max(
        available_propellant_kg - required_propellant_kg,
        0.0,
    )

    propellant_reserve_percent = (
        remaining_propellant_kg / available_propellant_kg * 100.0
        if available_propellant_kg > 0.0
        else 0.0
    )

    delta_v_margin_percent = (
        (available_delta_v - transfer.total_delta_v_m_s) / available_delta_v * 100.0
        if available_delta_v > 0.0
        else 0.0
    )

    safety_margin_percent = max(delta_v_margin_percent, 0.0)

    window_score = _calculate_window_score(
        feasible=feasible,
        propellant_reserve_percent=propellant_reserve_percent,
        minimum_propellant_reserve_percent=minimum_propellant_reserve_percent,
    )

    window_status = _determine_window_status(
        feasible=feasible,
        window_score=window_score,
    )

    warnings: list[str] = []

    if not feasible:
        warnings.append("INSUFFICIENT_DELTA_V")
    elif propellant_reserve_percent < minimum_propellant_reserve_percent + 5.0:
        warnings.append("LOW_PROPELLANT_MARGIN")

    maneuvers = _create_maneuvers(
        initial_altitude_m=initial_altitude_m,
        target_altitude_m=target_altitude_m,
        departure_delta_v_m_s=transfer.departure_delta_v_m_s,
        arrival_delta_v_m_s=transfer.arrival_delta_v_m_s,
        transfer_time_s=transfer.transfer_time_s,
    )

    return TrajectoryCalculationResult(
        feasible=feasible,
        required_delta_v_m_s=transfer.total_delta_v_m_s,
        available_delta_v_m_s=available_delta_v,
        estimated_propellant_kg=required_propellant_kg,
        propellant_reserve_percent=propellant_reserve_percent,
        safety_margin_percent=safety_margin_percent,
        estimated_duration_s=transfer.transfer_time_s,
        window_score=window_score,
        window_status=window_status,
        warnings=tuple(warnings),
        maneuvers=maneuvers,
    )


def _create_maneuvers(
    *,
    initial_altitude_m: float,
    target_altitude_m: float,
    departure_delta_v_m_s: float,
    arrival_delta_v_m_s: float,
    transfer_time_s: float,
) -> tuple[PlannedManeuverData, ...]:
    if initial_altitude_m == target_altitude_m:
        return ()

    maneuver_type = (
        ManeuverType.ORBIT_RAISE
        if target_altitude_m > initial_altitude_m
        else ManeuverType.ORBIT_LOWER
    )

    return (
        PlannedManeuverData(
            sequence=1,
            maneuver_type=maneuver_type,
            delta_v_m_s=departure_delta_v_m_s,
            planned_offset_s=0.0,
        ),
        PlannedManeuverData(
            sequence=2,
            maneuver_type=maneuver_type,
            delta_v_m_s=arrival_delta_v_m_s,
            planned_offset_s=transfer_time_s,
        ),
    )


def _calculate_window_score(
    *,
    feasible: bool,
    propellant_reserve_percent: float,
    minimum_propellant_reserve_percent: float,
) -> int:
    if not feasible:
        return 0

    if minimum_propellant_reserve_percent >= 100.0:
        return 0

    usable_range = 100.0 - minimum_propellant_reserve_percent

    normalized_margin = (
        propellant_reserve_percent - minimum_propellant_reserve_percent
    ) / usable_range

    return max(0, min(100, round(60 + 40 * normalized_margin)))


def _determine_window_status(
    *,
    feasible: bool,
    window_score: int,
) -> LaunchWindowStatus:
    if not feasible:
        return LaunchWindowStatus.INVALID

    if window_score < 70:
        return LaunchWindowStatus.VALID_WITH_RISK

    return LaunchWindowStatus.VALID
