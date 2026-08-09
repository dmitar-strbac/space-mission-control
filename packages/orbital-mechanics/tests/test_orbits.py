import pytest

from orbital_mechanics.constants import EARTH_MEAN_RADIUS_M
from orbital_mechanics.gravity import gravitational_acceleration
from orbital_mechanics.models import Vector2D
from orbital_mechanics.orbits import (
    hohmann_transfer,
    orbital_radius_from_altitude,
)
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


def test_hohmann_transfer_between_leo_orbits() -> None:
    initial_radius_m = orbital_radius_from_altitude(400_000.0)
    target_radius_m = orbital_radius_from_altitude(600_000.0)

    transfer = hohmann_transfer(
        initial_orbital_radius_m=initial_radius_m,
        target_orbital_radius_m=target_radius_m,
    )

    assert transfer.departure_delta_v_m_s > 0.0
    assert transfer.arrival_delta_v_m_s > 0.0
    assert transfer.total_delta_v_m_s == pytest.approx(
        transfer.departure_delta_v_m_s + transfer.arrival_delta_v_m_s
    )
    assert transfer.transfer_time_s > 0.0


def test_hohmann_transfer_same_orbit_requires_no_delta_v() -> None:
    radius_m = orbital_radius_from_altitude(400_000.0)

    transfer = hohmann_transfer(
        initial_orbital_radius_m=radius_m,
        target_orbital_radius_m=radius_m,
    )

    assert transfer.departure_delta_v_m_s == 0.0
    assert transfer.arrival_delta_v_m_s == 0.0
    assert transfer.total_delta_v_m_s == 0.0
    assert transfer.transfer_time_s == 0.0


def test_hohmann_transfer_is_symmetric_in_total_delta_v() -> None:
    lower_radius_m = orbital_radius_from_altitude(400_000.0)
    upper_radius_m = orbital_radius_from_altitude(800_000.0)

    raise_transfer = hohmann_transfer(
        initial_orbital_radius_m=lower_radius_m,
        target_orbital_radius_m=upper_radius_m,
    )

    lower_transfer = hohmann_transfer(
        initial_orbital_radius_m=upper_radius_m,
        target_orbital_radius_m=lower_radius_m,
    )

    assert raise_transfer.total_delta_v_m_s == pytest.approx(lower_transfer.total_delta_v_m_s)
