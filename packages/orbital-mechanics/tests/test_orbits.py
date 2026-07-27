import pytest

from orbital_mechanics.constants import EARTH_MEAN_RADIUS_M
from orbital_mechanics.gravity import gravitational_acceleration
from orbital_mechanics.models import Vector2D
from orbital_mechanics.units import kilometres_to_metres


def test_gravity_points_toward_earth_centre() -> None:
    position = Vector2D(
        x=EARTH_MEAN_RADIUS_M + kilometres_to_metres(400.0),
        y=0.0,
    )

    acceleration = gravitational_acceleration(position)

    assert acceleration.x < 0.0
    assert acceleration.y == pytest.approx(0.0)


def test_gravity_at_400_km_has_physically_reasonable_magnitude() -> None:
    position = Vector2D(
        x=EARTH_MEAN_RADIUS_M + kilometres_to_metres(400.0),
        y=0.0,
    )

    acceleration = gravitational_acceleration(position)

    assert acceleration.magnitude == pytest.approx(8.69, rel=0.01)


def test_gravity_is_symmetric_for_opposite_positions() -> None:
    radius_m = EARTH_MEAN_RADIUS_M + kilometres_to_metres(400.0)

    positive_position_acceleration = gravitational_acceleration(Vector2D(x=radius_m, y=0.0))
    negative_position_acceleration = gravitational_acceleration(Vector2D(x=-radius_m, y=0.0))

    assert positive_position_acceleration.x == pytest.approx(-negative_position_acceleration.x)
    assert positive_position_acceleration.y == pytest.approx(-negative_position_acceleration.y)


def test_gravity_is_undefined_at_coordinate_origin() -> None:
    with pytest.raises(ValueError, match="undefined at the origin"):
        gravitational_acceleration(Vector2D(x=0.0, y=0.0))
