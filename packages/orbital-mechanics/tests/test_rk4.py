import pytest

from orbital_mechanics.dynamics import StateDerivative
from orbital_mechanics.integrators.rk4 import rk4_step
from orbital_mechanics.models import StateVector, Vector2D


def test_rk4_propagates_constant_velocity_motion() -> None:
    initial_state = StateVector(
        position=Vector2D(x=0.0, y=0.0),
        velocity=Vector2D(x=10.0, y=-2.0),
        total_mass_kg=1_000.0,
        propellant_mass_kg=100.0,
    )

    def constant_velocity_derivative(
        state: StateVector,
    ) -> StateDerivative:
        return StateDerivative(
            position_rate_m_s=state.velocity,
            velocity_rate_m_s2=Vector2D(x=0.0, y=0.0),
            total_mass_rate_kg_s=0.0,
            propellant_mass_rate_kg_s=0.0,
        )

    result = rk4_step(
        state=initial_state,
        time_step_s=10.0,
        derivative_function=constant_velocity_derivative,
    )

    assert result.position.x == pytest.approx(100.0)
    assert result.position.y == pytest.approx(-20.0)
    assert result.velocity == initial_state.velocity
    assert result.total_mass_kg == pytest.approx(1_000.0)
    assert result.propellant_mass_kg == pytest.approx(100.0)
    assert result.elapsed_time_s == pytest.approx(10.0)


def test_rk4_updates_total_and_propellant_mass_equally() -> None:
    initial_state = StateVector(
        position=Vector2D(x=1.0, y=0.0),
        velocity=Vector2D(x=0.0, y=0.0),
        total_mass_kg=1_000.0,
        propellant_mass_kg=100.0,
    )

    def constant_consumption_derivative(
        _: StateVector,
    ) -> StateDerivative:
        return StateDerivative(
            position_rate_m_s=Vector2D(x=0.0, y=0.0),
            velocity_rate_m_s2=Vector2D(x=0.0, y=0.0),
            total_mass_rate_kg_s=-2.0,
            propellant_mass_rate_kg_s=-2.0,
        )

    result = rk4_step(
        state=initial_state,
        time_step_s=10.0,
        derivative_function=constant_consumption_derivative,
    )

    assert result.total_mass_kg == pytest.approx(980.0)
    assert result.propellant_mass_kg == pytest.approx(80.0)
    assert result.dry_mass_kg == pytest.approx(initial_state.dry_mass_kg)


def test_rk4_rejects_time_step_that_exhausts_propellant() -> None:
    initial_state = StateVector(
        position=Vector2D(x=1.0, y=0.0),
        velocity=Vector2D(x=0.0, y=0.0),
        total_mass_kg=1_000.0,
        propellant_mass_kg=10.0,
    )

    def excessive_consumption_derivative(
        _: StateVector,
    ) -> StateDerivative:
        return StateDerivative(
            position_rate_m_s=Vector2D(x=0.0, y=0.0),
            velocity_rate_m_s2=Vector2D(x=0.0, y=0.0),
            total_mass_rate_kg_s=-100.0,
            propellant_mass_rate_kg_s=-100.0,
        )

    with pytest.raises(ValueError, match="more propellant than available"):
        rk4_step(
            state=initial_state,
            time_step_s=1.0,
            derivative_function=excessive_consumption_derivative,
        )


@pytest.mark.parametrize(
    "time_step_s",
    [
        0.0,
        -1.0,
        float("inf"),
        float("nan"),
    ],
)
def test_rk4_rejects_invalid_time_step(time_step_s: float) -> None:
    initial_state = StateVector(
        position=Vector2D(x=1.0, y=0.0),
        velocity=Vector2D(x=0.0, y=0.0),
        total_mass_kg=1_000.0,
        propellant_mass_kg=100.0,
    )

    def derivative(_: StateVector) -> StateDerivative:
        return StateDerivative(
            position_rate_m_s=Vector2D(x=0.0, y=0.0),
            velocity_rate_m_s2=Vector2D(x=0.0, y=0.0),
            total_mass_rate_kg_s=0.0,
            propellant_mass_rate_kg_s=0.0,
        )

    with pytest.raises(ValueError, match="time step"):
        rk4_step(
            state=initial_state,
            time_step_s=time_step_s,
            derivative_function=derivative,
        )
