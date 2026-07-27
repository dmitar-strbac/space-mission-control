import pytest

from orbital_mechanics.models import StateVector, Vector2D


def test_vector_magnitude_uses_euclidean_distance() -> None:
    vector = Vector2D(x=3.0, y=4.0)

    assert vector.magnitude == pytest.approx(5.0)


def test_vector_normalization_preserves_direction() -> None:
    normalized = Vector2D(x=3.0, y=4.0).normalized()

    assert normalized.x == pytest.approx(0.6)
    assert normalized.y == pytest.approx(0.8)
    assert normalized.magnitude == pytest.approx(1.0)


def test_zero_vector_cannot_be_normalized() -> None:
    with pytest.raises(ValueError, match="zero vector"):
        Vector2D(x=0.0, y=0.0).normalized()


def test_vector_arithmetic_returns_new_vectors() -> None:
    first = Vector2D(x=4.0, y=2.0)
    second = Vector2D(x=1.0, y=3.0)

    assert first + second == Vector2D(x=5.0, y=5.0)
    assert first - second == Vector2D(x=3.0, y=-1.0)
    assert first * 2.0 == Vector2D(x=8.0, y=4.0)
    assert first / 2.0 == Vector2D(x=2.0, y=1.0)


def test_state_vector_exposes_derived_mass_distance_and_speed() -> None:
    state = StateVector(
        position=Vector2D(x=3.0, y=4.0),
        velocity=Vector2D(x=6.0, y=8.0),
        total_mass_kg=12_000.0,
        propellant_mass_kg=2_000.0,
        elapsed_time_s=15.0,
    )

    assert state.dry_mass_kg == pytest.approx(10_000.0)
    assert state.distance_from_origin_m == pytest.approx(5.0)
    assert state.speed_m_s == pytest.approx(10.0)


@pytest.mark.parametrize(
    ("total_mass_kg", "propellant_mass_kg", "elapsed_time_s", "error_message"),
    [
        (0.0, 0.0, 0.0, "Total spacecraft mass"),
        (1_000.0, -1.0, 0.0, "Propellant mass cannot be negative"),
        (1_000.0, 1_001.0, 0.0, "Propellant mass cannot exceed"),
        (1_000.0, 100.0, -1.0, "Elapsed simulation time"),
    ],
)
def test_state_vector_rejects_invalid_physical_values(
    total_mass_kg: float,
    propellant_mass_kg: float,
    elapsed_time_s: float,
    error_message: str,
) -> None:
    with pytest.raises(ValueError, match=error_message):
        StateVector(
            position=Vector2D(x=1.0, y=0.0),
            velocity=Vector2D(x=0.0, y=1.0),
            total_mass_kg=total_mass_kg,
            propellant_mass_kg=propellant_mass_kg,
            elapsed_time_s=elapsed_time_s,
        )
