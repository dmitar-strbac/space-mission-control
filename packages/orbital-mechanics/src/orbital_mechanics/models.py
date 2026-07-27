from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isfinite


@dataclass(frozen=True, slots=True)
class Vector2D:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not isfinite(self.x) or not isfinite(self.y):
            raise ValueError("Vector components must be finite numbers.")

    @property
    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    def normalized(self) -> Vector2D:
        magnitude = self.magnitude

        if magnitude == 0.0:
            raise ValueError("A zero vector cannot be normalized.")

        return self / magnitude

    def dot(self, other: Vector2D) -> float:
        return self.x * other.x + self.y * other.y

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(
            x=self.x + other.x,
            y=self.y + other.y,
        )

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(
            x=self.x - other.x,
            y=self.y - other.y,
        )

    def __mul__(self, scalar: float) -> Vector2D:
        if not isfinite(scalar):
            raise ValueError("Vector scalar must be a finite number.")

        return Vector2D(
            x=self.x * scalar,
            y=self.y * scalar,
        )

    def __rmul__(self, scalar: float) -> Vector2D:
        return self * scalar

    def __truediv__(self, scalar: float) -> Vector2D:
        if not isfinite(scalar):
            raise ValueError("Vector scalar must be a finite number.")

        if scalar == 0.0:
            raise ZeroDivisionError("A vector cannot be divided by zero.")

        return Vector2D(
            x=self.x / scalar,
            y=self.y / scalar,
        )


@dataclass(frozen=True, slots=True)
class StateVector:
    position: Vector2D
    velocity: Vector2D
    total_mass_kg: float
    propellant_mass_kg: float
    elapsed_time_s: float = 0.0

    def __post_init__(self) -> None:
        numeric_values = (
            self.total_mass_kg,
            self.propellant_mass_kg,
            self.elapsed_time_s,
        )

        if not all(isfinite(value) for value in numeric_values):
            raise ValueError("State vector values must be finite numbers.")

        if self.total_mass_kg <= 0.0:
            raise ValueError("Total spacecraft mass must be greater than zero.")

        if self.propellant_mass_kg < 0.0:
            raise ValueError("Propellant mass cannot be negative.")

        if self.propellant_mass_kg > self.total_mass_kg:
            raise ValueError("Propellant mass cannot exceed total spacecraft mass.")

        if self.elapsed_time_s < 0.0:
            raise ValueError("Elapsed simulation time cannot be negative.")

    @property
    def dry_mass_kg(self) -> float:
        return self.total_mass_kg - self.propellant_mass_kg

    @property
    def distance_from_origin_m(self) -> float:
        return self.position.magnitude

    @property
    def speed_m_s(self) -> float:
        return self.velocity.magnitude
