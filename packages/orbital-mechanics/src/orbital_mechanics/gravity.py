from math import isfinite

from orbital_mechanics.constants import EARTH_GRAVITATIONAL_PARAMETER_M3_S2
from orbital_mechanics.models import Vector2D


def gravitational_acceleration(
    position: Vector2D,
    gravitational_parameter_m3_s2: float = EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
) -> Vector2D:
    if not isfinite(gravitational_parameter_m3_s2) or gravitational_parameter_m3_s2 <= 0.0:
        raise ValueError("Gravitational parameter must be a positive finite number.")

    radius_m = position.magnitude

    if radius_m == 0.0:
        raise ValueError("Gravitational acceleration is undefined at the origin.")

    acceleration_factor = -gravitational_parameter_m3_s2 / radius_m**3

    return position * acceleration_factor
