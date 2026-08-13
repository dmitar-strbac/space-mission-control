from app.domain.validation import (
    validate_final_resources,
)


def test_final_resources_are_valid_with_sufficient_capacity() -> None:
    result = validate_final_resources(
        total_mass_kg=10_000.0,
        required_propellant_kg=1_000.0,
        propellant_capacity_kg=2_000.0,
        minimum_propellant_reserve_percent=10.0,
        mission_duration_s=3_600.0,
        oxygen_capacity_kg=100.0,
        oxygen_consumption_rate_kg_s=0.001,
        battery_capacity_kwh=100.0,
        power_consumption_kw=10.0,
        engine_thrust_n=100_000.0,
        max_acceleration_g=3.0,
    )

    assert result.valid
    assert not result.violations


def test_final_resources_detect_insufficient_propellant() -> None:
    result = validate_final_resources(
        total_mass_kg=10_000.0,
        required_propellant_kg=1_900.0,
        propellant_capacity_kg=2_000.0,
        minimum_propellant_reserve_percent=10.0,
        mission_duration_s=3_600.0,
        oxygen_capacity_kg=100.0,
        oxygen_consumption_rate_kg_s=0.001,
        battery_capacity_kwh=100.0,
        power_consumption_kw=10.0,
        engine_thrust_n=100_000.0,
        max_acceleration_g=3.0,
    )

    assert not result.valid

    codes = {violation.code.value for violation in result.violations}

    assert "INSUFFICIENT_PROPELLANT" in codes


def test_final_resources_detect_operational_limits() -> None:
    result = validate_final_resources(
        total_mass_kg=1_000.0,
        required_propellant_kg=100.0,
        propellant_capacity_kg=1_000.0,
        minimum_propellant_reserve_percent=10.0,
        mission_duration_s=10_000.0,
        oxygen_capacity_kg=1.0,
        oxygen_consumption_rate_kg_s=0.01,
        battery_capacity_kwh=1.0,
        power_consumption_kw=10.0,
        engine_thrust_n=100_000.0,
        max_acceleration_g=1.0,
    )

    assert not result.valid

    codes = {violation.code.value for violation in result.violations}

    assert "INSUFFICIENT_OXYGEN" in codes
    assert "INSUFFICIENT_ENERGY" in codes
    assert "MAX_ACCELERATION_EXCEEDED" in codes
