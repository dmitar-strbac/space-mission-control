from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite

from orbital_mechanics.gravity import gravitational_acceleration
from orbital_mechanics.models import (
    EngineParameters,
    StateVector,
    ThrustCommand,
    Vector2D,
)
from orbital_mechanics.propulsion import (
    mass_flow_rate_kg_s,
    thrust_acceleration_m_s2,
)


@dataclass(frozen=True, slots=True)
class StateDerivative:
    position_rate_m_s: Vector2D
    velocity_rate_m_s2: Vector2D
    total_mass_rate_kg_s: float
    propellant_mass_rate_kg_s: float
    elapsed_time_rate: float = 1.0

    def __post_init__(self) -> None:
        numeric_values = (
            self.total_mass_rate_kg_s,
            self.propellant_mass_rate_kg_s,
            self.elapsed_time_rate,
        )

        if not all(isfinite(value) for value in numeric_values):
            raise ValueError("State derivative values must be finite numbers.")

        if self.elapsed_time_rate <= 0.0:
            raise ValueError("Elapsed time rate must be greater than zero.")


StateDerivativeFunction = Callable[[StateVector], StateDerivative]


def calculate_state_derivative(
    state: StateVector,
    engine: EngineParameters | None = None,
    thrust_command: ThrustCommand | None = None,
) -> StateDerivative:
    if (engine is None) != (thrust_command is None):
        raise ValueError("Engine parameters and thrust command must be provided together.")

    gravity_acceleration = gravitational_acceleration(state.position)
    engine_acceleration = Vector2D(x=0.0, y=0.0)
    propellant_rate_kg_s = 0.0

    if (
        engine is not None
        and thrust_command is not None
        and state.propellant_mass_kg > 0.0
        and thrust_command.throttle > 0.0
    ):
        engine_acceleration = thrust_acceleration_m_s2(
            command=thrust_command,
            engine=engine,
            total_mass_kg=state.total_mass_kg,
        )
        propellant_rate_kg_s = -mass_flow_rate_kg_s(
            engine=engine,
            throttle=thrust_command.throttle,
        )

    return StateDerivative(
        position_rate_m_s=state.velocity,
        velocity_rate_m_s2=gravity_acceleration + engine_acceleration,
        total_mass_rate_kg_s=propellant_rate_kg_s,
        propellant_mass_rate_kg_s=propellant_rate_kg_s,
    )


def create_dynamics_function(
    engine: EngineParameters | None = None,
    thrust_command: ThrustCommand | None = None,
) -> StateDerivativeFunction:
    if (engine is None) != (thrust_command is None):
        raise ValueError("Engine parameters and thrust command must be provided together.")

    def derivative(state: StateVector) -> StateDerivative:
        return calculate_state_derivative(
            state=state,
            engine=engine,
            thrust_command=thrust_command,
        )

    return derivative
