import pytest

from orbital_mechanics.dynamics import create_dynamics_function
from orbital_mechanics.integrators.rk4 import rk4_step
from orbital_mechanics.models import StateVector
from orbital_mechanics.orbits import (
    circular_orbit_period,
    create_circular_orbit_state,
    orbital_altitude,
    specific_orbital_energy,
)
from orbital_mechanics.units import kilometres_to_metres


def propagate_for_duration(
    initial_state: StateVector,
    duration_s: float,
    time_step_s: float,
) -> StateVector:
    state = initial_state
    remaining_duration_s = duration_s
    derivative_function = create_dynamics_function()

    while remaining_duration_s > 0.0:
        current_step_s = min(time_step_s, remaining_duration_s)

        state = rk4_step(
            state=state,
            time_step_s=current_step_s,
            derivative_function=derivative_function,
        )

        remaining_duration_s -= current_step_s

    return state


def test_400_km_circular_leo_remains_stable_for_one_orbit() -> None:
    altitude_m = kilometres_to_metres(400.0)
    initial_state = create_circular_orbit_state(
        altitude_m=altitude_m,
        total_mass_kg=12_000.0,
        propellant_mass_kg=2_000.0,
    )
    orbital_period_s = circular_orbit_period(initial_state.distance_from_origin_m)

    final_state = propagate_for_duration(
        initial_state=initial_state,
        duration_s=orbital_period_s,
        time_step_s=10.0,
    )

    final_altitude_m = orbital_altitude(final_state.position)
    final_position_error_m = (final_state.position - initial_state.position).magnitude
    final_velocity_error_m_s = (final_state.velocity - initial_state.velocity).magnitude

    assert final_altitude_m == pytest.approx(altitude_m, abs=1_000.0)
    assert final_position_error_m < 10_000.0
    assert final_velocity_error_m_s < 15.0
    assert final_state.elapsed_time_s == pytest.approx(orbital_period_s)
    assert final_state.total_mass_kg == pytest.approx(initial_state.total_mass_kg)
    assert final_state.propellant_mass_kg == pytest.approx(initial_state.propellant_mass_kg)


def test_specific_orbital_energy_is_approximately_conserved() -> None:
    initial_state = create_circular_orbit_state(
        altitude_m=kilometres_to_metres(400.0),
        total_mass_kg=12_000.0,
        propellant_mass_kg=2_000.0,
    )
    orbital_period_s = circular_orbit_period(initial_state.distance_from_origin_m)

    initial_energy = specific_orbital_energy(
        position=initial_state.position,
        velocity=initial_state.velocity,
    )

    final_state = propagate_for_duration(
        initial_state=initial_state,
        duration_s=orbital_period_s,
        time_step_s=10.0,
    )

    final_energy = specific_orbital_energy(
        position=final_state.position,
        velocity=final_state.velocity,
    )

    assert final_energy == pytest.approx(initial_energy, rel=1e-6)
