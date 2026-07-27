from math import isfinite, pi, sqrt

from orbital_mechanics.constants import (
    EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
    EARTH_MEAN_RADIUS_M,
)
from orbital_mechanics.models import StateVector, Vector2D


def orbital_radius_from_altitude(
    altitude_m: float,
    central_body_radius_m: float = EARTH_MEAN_RADIUS_M,
) -> float:
    if not isfinite(altitude_m) or altitude_m < 0.0:
        raise ValueError("Orbital altitude must be a non-negative finite number.")

    if not isfinite(central_body_radius_m) or central_body_radius_m <= 0.0:
        raise ValueError("Central body radius must be a positive finite number.")

    return central_body_radius_m + altitude_m


def orbital_altitude(
    position: Vector2D,
    central_body_radius_m: float = EARTH_MEAN_RADIUS_M,
) -> float:
    if not isfinite(central_body_radius_m) or central_body_radius_m <= 0.0:
        raise ValueError("Central body radius must be a positive finite number.")

    altitude_m = position.magnitude - central_body_radius_m

    if altitude_m < 0.0:
        raise ValueError("Position is located below the central body's surface.")

    return altitude_m


def circular_orbit_velocity(
    orbital_radius_m: float,
    gravitational_parameter_m3_s2: float = EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
) -> float:
    _validate_orbital_parameters(
        orbital_radius_m=orbital_radius_m,
        gravitational_parameter_m3_s2=gravitational_parameter_m3_s2,
    )

    return sqrt(gravitational_parameter_m3_s2 / orbital_radius_m)


def circular_orbit_period(
    orbital_radius_m: float,
    gravitational_parameter_m3_s2: float = EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
) -> float:
    _validate_orbital_parameters(
        orbital_radius_m=orbital_radius_m,
        gravitational_parameter_m3_s2=gravitational_parameter_m3_s2,
    )

    return 2.0 * pi * sqrt(orbital_radius_m**3 / gravitational_parameter_m3_s2)


def specific_orbital_energy(
    position: Vector2D,
    velocity: Vector2D,
    gravitational_parameter_m3_s2: float = EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
) -> float:
    if not isfinite(gravitational_parameter_m3_s2) or gravitational_parameter_m3_s2 <= 0.0:
        raise ValueError("Gravitational parameter must be a positive finite number.")

    orbital_radius_m = position.magnitude

    if orbital_radius_m == 0.0:
        raise ValueError("Specific orbital energy is undefined at the origin.")

    kinetic_energy_j_kg = velocity.magnitude**2 / 2.0
    gravitational_potential_j_kg = gravitational_parameter_m3_s2 / orbital_radius_m

    return kinetic_energy_j_kg - gravitational_potential_j_kg


def create_circular_orbit_state(
    altitude_m: float,
    total_mass_kg: float,
    propellant_mass_kg: float,
) -> StateVector:
    orbital_radius_m = orbital_radius_from_altitude(altitude_m)
    orbital_velocity_m_s = circular_orbit_velocity(orbital_radius_m)

    return StateVector(
        position=Vector2D(x=orbital_radius_m, y=0.0),
        velocity=Vector2D(x=0.0, y=orbital_velocity_m_s),
        total_mass_kg=total_mass_kg,
        propellant_mass_kg=propellant_mass_kg,
    )


def _validate_orbital_parameters(
    orbital_radius_m: float,
    gravitational_parameter_m3_s2: float,
) -> None:
    if not isfinite(orbital_radius_m) or orbital_radius_m <= 0.0:
        raise ValueError("Orbital radius must be a positive finite number.")

    if not isfinite(gravitational_parameter_m3_s2) or gravitational_parameter_m3_s2 <= 0.0:
        raise ValueError("Gravitational parameter must be a positive finite number.")
