import pytest

from orbital_mechanics.constants import STANDARD_GRAVITY_M_S2
from orbital_mechanics.models import (
    EngineParameters,
    ThrustCommand,
    Vector2D,
)
from orbital_mechanics.propulsion import (
    available_delta_v_m_s,
    mass_flow_rate_kg_s,
    propellant_consumed_kg,
    required_propellant_mass_kg,
    thrust_acceleration_m_s2,
)


def test_mass_flow_rate_matches_engine_equation() -> None:
    engine = EngineParameters(
        thrust_n=100_000.0,
        specific_impulse_s=300.0,
    )

    result = mass_flow_rate_kg_s(engine)

    expected = 100_000.0 / (300.0 * STANDARD_GRAVITY_M_S2)

    assert result == pytest.approx(expected)


def test_half_throttle_produces_half_mass_flow() -> None:
    engine = EngineParameters(
        thrust_n=100_000.0,
        specific_impulse_s=300.0,
    )

    full_throttle_flow = mass_flow_rate_kg_s(engine, throttle=1.0)
    half_throttle_flow = mass_flow_rate_kg_s(engine, throttle=0.5)

    assert half_throttle_flow == pytest.approx(full_throttle_flow / 2.0)


def test_available_delta_v_is_zero_without_propellant() -> None:
    result = available_delta_v_m_s(
        total_mass_kg=10_000.0,
        propellant_mass_kg=0.0,
        specific_impulse_s=300.0,
    )

    assert result == pytest.approx(0.0)


def test_more_propellant_provides_more_available_delta_v() -> None:
    low_propellant_delta_v = available_delta_v_m_s(
        total_mass_kg=10_000.0,
        propellant_mass_kg=1_000.0,
        specific_impulse_s=300.0,
    )
    high_propellant_delta_v = available_delta_v_m_s(
        total_mass_kg=10_000.0,
        propellant_mass_kg=3_000.0,
        specific_impulse_s=300.0,
    )

    assert high_propellant_delta_v > low_propellant_delta_v


def test_propellant_consumption_is_limited_by_available_amount() -> None:
    engine = EngineParameters(
        thrust_n=100_000.0,
        specific_impulse_s=300.0,
    )

    consumed_kg = propellant_consumed_kg(
        engine=engine,
        burn_duration_s=100.0,
        available_propellant_kg=50.0,
    )

    assert consumed_kg == pytest.approx(50.0)


def test_thrust_acceleration_follows_requested_direction() -> None:
    engine = EngineParameters(
        thrust_n=20_000.0,
        specific_impulse_s=300.0,
    )
    command = ThrustCommand(
        direction=Vector2D(x=0.0, y=10.0),
        throttle=1.0,
    )

    acceleration = thrust_acceleration_m_s2(
        command=command,
        engine=engine,
        total_mass_kg=10_000.0,
    )

    assert acceleration.x == pytest.approx(0.0)
    assert acceleration.y == pytest.approx(2.0)


@pytest.mark.parametrize(
    "throttle",
    [
        -0.1,
        1.1,
        float("inf"),
        float("nan"),
    ],
)
def test_mass_flow_rejects_invalid_throttle(throttle: float) -> None:
    engine = EngineParameters(
        thrust_n=100_000.0,
        specific_impulse_s=300.0,
    )

    with pytest.raises(ValueError, match="Throttle"):
        mass_flow_rate_kg_s(engine=engine, throttle=throttle)


def test_required_propellant_is_zero_for_zero_delta_v() -> None:
    result = required_propellant_mass_kg(
        total_mass_kg=10_000.0,
        required_delta_v_m_s=0.0,
        specific_impulse_s=450.0,
    )

    assert result == 0.0


def test_required_propellant_increases_with_delta_v() -> None:
    low_delta_v = required_propellant_mass_kg(
        total_mass_kg=10_000.0,
        required_delta_v_m_s=100.0,
        specific_impulse_s=450.0,
    )

    high_delta_v = required_propellant_mass_kg(
        total_mass_kg=10_000.0,
        required_delta_v_m_s=500.0,
        specific_impulse_s=450.0,
    )

    assert high_delta_v > low_delta_v > 0.0


def test_required_propellant_rejects_negative_delta_v() -> None:
    with pytest.raises(
        ValueError,
        match="Required delta-v",
    ):
        required_propellant_mass_kg(
            total_mass_kg=10_000.0,
            required_delta_v_m_s=-1.0,
            specific_impulse_s=450.0,
        )
