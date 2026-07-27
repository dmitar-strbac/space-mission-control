from math import isfinite

from orbital_mechanics.dynamics import (
    StateDerivative,
    StateDerivativeFunction,
)
from orbital_mechanics.models import StateVector, Vector2D

_PROPELLANT_TOLERANCE_KG = 1e-9


def rk4_step(
    state: StateVector,
    time_step_s: float,
    derivative_function: StateDerivativeFunction,
) -> StateVector:
    if not isfinite(time_step_s) or time_step_s <= 0.0:
        raise ValueError("Integration time step must be a positive finite number.")

    first_derivative = derivative_function(state)

    second_state = _offset_state(
        state=state,
        derivative=first_derivative,
        duration_s=time_step_s / 2.0,
    )
    second_derivative = derivative_function(second_state)

    third_state = _offset_state(
        state=state,
        derivative=second_derivative,
        duration_s=time_step_s / 2.0,
    )
    third_derivative = derivative_function(third_state)

    fourth_state = _offset_state(
        state=state,
        derivative=third_derivative,
        duration_s=time_step_s,
    )
    fourth_derivative = derivative_function(fourth_state)

    average_derivative = _weighted_average(
        first=first_derivative,
        second=second_derivative,
        third=third_derivative,
        fourth=fourth_derivative,
    )

    return _offset_state(
        state=state,
        derivative=average_derivative,
        duration_s=time_step_s,
    )


def _offset_state(
    state: StateVector,
    derivative: StateDerivative,
    duration_s: float,
) -> StateVector:
    total_mass_kg = state.total_mass_kg + derivative.total_mass_rate_kg_s * duration_s
    propellant_mass_kg = (
        state.propellant_mass_kg + derivative.propellant_mass_rate_kg_s * duration_s
    )

    if propellant_mass_kg < -_PROPELLANT_TOLERANCE_KG:
        raise ValueError("Integration time step would consume more propellant than available.")

    if total_mass_kg <= 0.0:
        raise ValueError("Integration time step would reduce total spacecraft mass below zero.")

    propellant_mass_kg = max(0.0, propellant_mass_kg)

    return StateVector(
        position=state.position + derivative.position_rate_m_s * duration_s,
        velocity=state.velocity + derivative.velocity_rate_m_s2 * duration_s,
        total_mass_kg=total_mass_kg,
        propellant_mass_kg=propellant_mass_kg,
        elapsed_time_s=state.elapsed_time_s + derivative.elapsed_time_rate * duration_s,
    )


def _weighted_average(
    first: StateDerivative,
    second: StateDerivative,
    third: StateDerivative,
    fourth: StateDerivative,
) -> StateDerivative:
    return StateDerivative(
        position_rate_m_s=_weighted_vector_average(
            first.position_rate_m_s,
            second.position_rate_m_s,
            third.position_rate_m_s,
            fourth.position_rate_m_s,
        ),
        velocity_rate_m_s2=_weighted_vector_average(
            first.velocity_rate_m_s2,
            second.velocity_rate_m_s2,
            third.velocity_rate_m_s2,
            fourth.velocity_rate_m_s2,
        ),
        total_mass_rate_kg_s=_weighted_scalar_average(
            first.total_mass_rate_kg_s,
            second.total_mass_rate_kg_s,
            third.total_mass_rate_kg_s,
            fourth.total_mass_rate_kg_s,
        ),
        propellant_mass_rate_kg_s=_weighted_scalar_average(
            first.propellant_mass_rate_kg_s,
            second.propellant_mass_rate_kg_s,
            third.propellant_mass_rate_kg_s,
            fourth.propellant_mass_rate_kg_s,
        ),
        elapsed_time_rate=_weighted_scalar_average(
            first.elapsed_time_rate,
            second.elapsed_time_rate,
            third.elapsed_time_rate,
            fourth.elapsed_time_rate,
        ),
    )


def _weighted_vector_average(
    first: Vector2D,
    second: Vector2D,
    third: Vector2D,
    fourth: Vector2D,
) -> Vector2D:
    return (first + second * 2.0 + third * 2.0 + fourth) / 6.0


def _weighted_scalar_average(
    first: float,
    second: float,
    third: float,
    fourth: float,
) -> float:
    return (first + 2.0 * second + 2.0 * third + fourth) / 6.0
