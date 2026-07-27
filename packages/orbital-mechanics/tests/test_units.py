import pytest

from orbital_mechanics.units import (
    kilometres_per_second_to_metres_per_second,
    kilometres_to_metres,
    metres_per_second_to_kilometres_per_second,
    metres_to_kilometres,
    minutes_to_seconds,
    seconds_to_minutes,
)


def test_distance_conversions_are_inverse_operations() -> None:
    distance_km = 400.0

    distance_m = kilometres_to_metres(distance_km)

    assert distance_m == pytest.approx(400_000.0)
    assert metres_to_kilometres(distance_m) == pytest.approx(distance_km)


def test_velocity_conversions_are_inverse_operations() -> None:
    velocity_km_s = 7.67

    velocity_m_s = kilometres_per_second_to_metres_per_second(velocity_km_s)

    assert velocity_m_s == pytest.approx(7_670.0)
    assert metres_per_second_to_kilometres_per_second(velocity_m_s) == pytest.approx(velocity_km_s)


def test_time_conversions_are_inverse_operations() -> None:
    duration_min = 92.5

    duration_s = minutes_to_seconds(duration_min)

    assert duration_s == pytest.approx(5_550.0)
    assert seconds_to_minutes(duration_s) == pytest.approx(duration_min)
