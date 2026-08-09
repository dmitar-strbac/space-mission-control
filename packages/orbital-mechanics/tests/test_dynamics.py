import pytest

from orbital_mechanics.constants import EARTH_MEAN_RADIUS_M
from orbital_mechanics.dynamics import calculate_state_derivative
from orbital_mechanics.models import (
    EngineParameters,
    StateVector,
    ThrustCommand,
    Vector2D,
)
from orbital_mechanics.units import kilometres_to_metres


def create_test_state() -> StateVector:
    return StateVector(
        position=Vector2D(
            x=EARTH_MEAN_RADIUS_M + kilometres_to_metres(400.0),
            y=0.0,
        ),
        velocity=Vector2D(x=0.0, y=7_670.0),
        total_mass_kg=10_000.0,
        propellant_mass_kg=2_000.0,
    )


def test_coasting_state_is_affected_only_by_gravity() -> None:
    derivative = calculate_state_derivative(create_test_state())

    assert derivative.position_rate_m_s == Vector2D(x=0.0, y=7_670.0)
    assert derivative.velocity_rate_m_s2.x < 0.0
    assert derivative.velocity_rate_m_s2.y == pytest.approx(0.0)
    assert derivative.total_mass_rate_kg_s == pytest.approx(0.0)
    assert derivative.propellant_mass_rate_kg_s == pytest.approx(0.0)


def test_active_engine_adds_acceleration_and_consumes_propellant() -> None:
    state = create_test_state()
    engine = EngineParameters(
        thrust_n=20_000.0,
        specific_impulse_s=300.0,
    )
    command = ThrustCommand(
        direction=Vector2D(x=0.0, y=1.0),
        throttle=1.0,
    )

    derivative = calculate_state_derivative(
        state=state,
        engine=engine,
        thrust_command=command,
    )

    assert derivative.velocity_rate_m_s2.x < 0.0
    assert derivative.velocity_rate_m_s2.y == pytest.approx(2.0)
    assert derivative.total_mass_rate_kg_s < 0.0
    assert derivative.propellant_mass_rate_kg_s == pytest.approx(derivative.total_mass_rate_kg_s)


def test_engine_does_not_produce_thrust_without_propellant() -> None:
    state = StateVector(
        position=Vector2D(
            x=EARTH_MEAN_RADIUS_M + kilometres_to_metres(400.0),
            y=0.0,
        ),
        velocity=Vector2D(x=0.0, y=7_670.0),
        total_mass_kg=8_000.0,
        propellant_mass_kg=0.0,
    )
    engine = EngineParameters(
        thrust_n=20_000.0,
        specific_impulse_s=300.0,
    )
    command = ThrustCommand(
        direction=Vector2D(x=0.0, y=1.0),
    )

    derivative = calculate_state_derivative(
        state=state,
        engine=engine,
        thrust_command=command,
    )

    assert derivative.velocity_rate_m_s2.y == pytest.approx(0.0)
    assert derivative.total_mass_rate_kg_s == pytest.approx(0.0)
    assert derivative.propellant_mass_rate_kg_s == pytest.approx(0.0)


def test_engine_and_command_must_be_provided_together() -> None:
    engine = EngineParameters(
        thrust_n=20_000.0,
        specific_impulse_s=300.0,
    )

    with pytest.raises(ValueError, match="provided together"):
        calculate_state_derivative(
            state=create_test_state(),
            engine=engine,
        )
