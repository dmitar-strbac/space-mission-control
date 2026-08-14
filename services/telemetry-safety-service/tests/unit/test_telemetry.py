import pytest

from app.domain.telemetry import (
    EARTH_RADIUS_M,
    STANDARD_GRAVITY_M_S2,
    calculate_altitude_km,
    calculate_fuel_flow_kg_s,
    calculate_oxygen_remaining_h,
    calculate_percentage,
    calculate_power_remaining_h,
    calculate_remaining_delta_v_m_s,
    calculate_speed_km_s,
    calculate_vertical_speed_m_s,
)


def test_altitude_is_derived_from_position_vector() -> None:
    altitude = calculate_altitude_km(
        position_x_m=EARTH_RADIUS_M + 400_000.0,
        position_y_m=0.0,
    )

    assert altitude == pytest.approx(400.0)


def test_speed_is_converted_to_kilometers_per_second() -> None:
    speed = calculate_speed_km_s(
        velocity_x_m_s=0.0,
        velocity_y_m_s=7_670.0,
    )

    assert speed == pytest.approx(7.67)


def test_circular_orbit_has_zero_vertical_speed() -> None:
    vertical_speed = calculate_vertical_speed_m_s(
        position_x_m=EARTH_RADIUS_M + 400_000.0,
        position_y_m=0.0,
        velocity_x_m_s=0.0,
        velocity_y_m_s=7_670.0,
    )

    assert vertical_speed == pytest.approx(0.0)


def test_percentage_is_calculated_from_initial_capacity() -> None:
    percentage = calculate_percentage(
        current=25.0,
        initial=100.0,
    )

    assert percentage == pytest.approx(25.0)


def test_percentage_is_clamped_to_valid_range() -> None:
    assert calculate_percentage(
        current=120.0,
        initial=100.0,
    ) == pytest.approx(100.0)

    assert calculate_percentage(
        current=-10.0,
        initial=100.0,
    ) == pytest.approx(0.0)


def test_remaining_delta_v_uses_rocket_equation() -> None:
    delta_v = calculate_remaining_delta_v_m_s(
        total_mass_kg=10_000.0,
        propellant_kg=2_000.0,
        specific_impulse_s=320.0,
    )

    expected = 320.0 * STANDARD_GRAVITY_M_S2 * 0.22314355131420976

    assert delta_v == pytest.approx(expected)


def test_remaining_delta_v_is_zero_without_propellant() -> None:
    delta_v = calculate_remaining_delta_v_m_s(
        total_mass_kg=8_000.0,
        propellant_kg=0.0,
        specific_impulse_s=320.0,
    )

    assert delta_v == 0.0


def test_fuel_flow_is_derived_from_thrust_and_specific_impulse() -> None:
    flow = calculate_fuel_flow_kg_s(
        engine_thrust_n=100_000.0,
        specific_impulse_s=300.0,
    )

    expected = 100_000.0 / (300.0 * STANDARD_GRAVITY_M_S2)

    assert flow == pytest.approx(expected)


def test_inactive_engine_has_zero_fuel_flow() -> None:
    flow = calculate_fuel_flow_kg_s(
        engine_thrust_n=0.0,
        specific_impulse_s=300.0,
    )

    assert flow == 0.0


def test_oxygen_remaining_is_reported_in_hours() -> None:
    remaining = calculate_oxygen_remaining_h(
        oxygen_kg=36.0,
        consumption_rate_kg_s=0.001,
    )

    assert remaining == pytest.approx(10.0)


def test_unlimited_oxygen_estimate_when_consumption_is_zero() -> None:
    remaining = calculate_oxygen_remaining_h(
        oxygen_kg=36.0,
        consumption_rate_kg_s=0.0,
    )

    assert remaining is None


def test_power_remaining_uses_battery_energy_and_consumption() -> None:
    remaining = calculate_power_remaining_h(
        battery_kwh=50.0,
        power_consumption_kw=10.0,
    )

    assert remaining == pytest.approx(5.0)
