import pytest

from app.domain.enums import (
    LaunchWindowStatus,
    ManeuverType,
)
from app.domain.planning import (
    EARTH_RADIUS_M,
    calculate_leo_deorbit,
    calculate_leo_trajectory,
)


def test_orbit_raise_produces_two_maneuvers() -> None:
    result = calculate_leo_trajectory(
        initial_altitude_m=400_000.0,
        target_altitude_m=600_000.0,
        total_mass_kg=20_000.0,
        available_propellant_kg=8_000.0,
        engine_specific_impulse_s=450.0,
        minimum_propellant_reserve_percent=10.0,
    )

    assert result.feasible is True
    assert result.required_delta_v_m_s > 0.0
    assert result.estimated_propellant_kg > 0.0
    assert result.estimated_duration_s > 0.0

    assert len(result.maneuvers) == 2

    assert result.maneuvers[0].maneuver_type is ManeuverType.ORBIT_RAISE
    assert result.maneuvers[1].maneuver_type is ManeuverType.ORBIT_RAISE

    assert result.maneuvers[0].sequence == 1
    assert result.maneuvers[1].sequence == 2


def test_orbit_lower_produces_two_maneuvers() -> None:
    result = calculate_leo_trajectory(
        initial_altitude_m=600_000.0,
        target_altitude_m=400_000.0,
        total_mass_kg=20_000.0,
        available_propellant_kg=8_000.0,
        engine_specific_impulse_s=450.0,
        minimum_propellant_reserve_percent=10.0,
    )

    assert result.feasible is True
    assert len(result.maneuvers) == 2

    assert all(maneuver.maneuver_type is ManeuverType.ORBIT_LOWER for maneuver in result.maneuvers)


def test_same_orbit_requires_no_maneuver() -> None:
    result = calculate_leo_trajectory(
        initial_altitude_m=400_000.0,
        target_altitude_m=400_000.0,
        total_mass_kg=20_000.0,
        available_propellant_kg=8_000.0,
        engine_specific_impulse_s=450.0,
        minimum_propellant_reserve_percent=10.0,
    )

    assert result.feasible is True
    assert result.required_delta_v_m_s == pytest.approx(0.0)
    assert result.estimated_propellant_kg == pytest.approx(0.0)
    assert result.estimated_duration_s == pytest.approx(0.0)
    assert result.maneuvers == ()


def test_insufficient_propellant_marks_plan_infeasible() -> None:
    result = calculate_leo_trajectory(
        initial_altitude_m=200_000.0,
        target_altitude_m=2_000_000.0,
        total_mass_kg=10_000.0,
        available_propellant_kg=50.0,
        engine_specific_impulse_s=300.0,
        minimum_propellant_reserve_percent=10.0,
    )

    assert result.feasible is False
    assert result.window_status is LaunchWindowStatus.INVALID
    assert result.window_score == 0
    assert "INSUFFICIENT_DELTA_V" in result.warnings


def test_planning_result_is_deterministic() -> None:
    arguments = {
        "initial_altitude_m": 400_000.0,
        "target_altitude_m": 800_000.0,
        "total_mass_kg": 20_000.0,
        "available_propellant_kg": 8_000.0,
        "engine_specific_impulse_s": 450.0,
        "minimum_propellant_reserve_percent": 10.0,
    }

    first = calculate_leo_trajectory(**arguments)
    second = calculate_leo_trajectory(**arguments)

    assert first == second


def test_leo_deorbit_generates_retrograde_burn() -> None:
    result = calculate_leo_deorbit(
        position_x_m=(EARTH_RADIUS_M + 400_000.0),
        position_y_m=0.0,
        total_mass_kg=10_000.0,
        available_propellant_kg=2_000.0,
        engine_specific_impulse_s=320.0,
    )

    assert result.feasible is True
    assert result.required_delta_v_m_s > 0.0

    assert result.maneuver.maneuver_type is ManeuverType.DEORBIT_BURN

    assert result.maneuver.delta_v_m_s == pytest.approx(result.required_delta_v_m_s)

    assert result.estimated_propellant_kg > 0.0


def test_leo_deorbit_rejects_state_below_entry_interface() -> None:
    with pytest.raises(
        ValueError,
        match="already at or below",
    ):
        calculate_leo_deorbit(
            position_x_m=(EARTH_RADIUS_M + 100_000.0),
            position_y_m=0.0,
            total_mass_kg=10_000.0,
            available_propellant_kg=2_000.0,
            engine_specific_impulse_s=320.0,
        )


def test_leo_deorbit_reports_insufficient_propellant() -> None:
    result = calculate_leo_deorbit(
        position_x_m=(EARTH_RADIUS_M + 400_000.0),
        position_y_m=0.0,
        total_mass_kg=10_000.0,
        available_propellant_kg=0.01,
        engine_specific_impulse_s=320.0,
    )

    assert result.feasible is False

    assert result.estimated_propellant_kg > 0.01
