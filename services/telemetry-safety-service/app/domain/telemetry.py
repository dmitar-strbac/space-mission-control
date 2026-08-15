import math

STANDARD_GRAVITY_M_S2 = 9.80665
EARTH_RADIUS_M = 6_371_000.0


def vector_magnitude(
    x: float,
    y: float,
) -> float:
    return math.hypot(x, y)


def calculate_altitude_km(
    *,
    position_x_m: float,
    position_y_m: float,
) -> float:
    radius_m = vector_magnitude(
        position_x_m,
        position_y_m,
    )

    return (radius_m - EARTH_RADIUS_M) / 1000.0


def calculate_speed_km_s(
    *,
    velocity_x_m_s: float,
    velocity_y_m_s: float,
) -> float:
    return (
        vector_magnitude(
            velocity_x_m_s,
            velocity_y_m_s,
        )
        / 1000.0
    )


def calculate_vertical_speed_m_s(
    *,
    position_x_m: float,
    position_y_m: float,
    velocity_x_m_s: float,
    velocity_y_m_s: float,
) -> float:
    radius_m = vector_magnitude(
        position_x_m,
        position_y_m,
    )

    if radius_m == 0.0:
        return 0.0

    return (position_x_m * velocity_x_m_s + position_y_m * velocity_y_m_s) / radius_m


def calculate_percentage(
    *,
    current: float,
    initial: float,
) -> float:
    if initial <= 0.0:
        return 0.0

    return max(
        0.0,
        min(
            100.0,
            current / initial * 100.0,
        ),
    )


def calculate_remaining_delta_v_m_s(
    *,
    total_mass_kg: float,
    propellant_kg: float,
    specific_impulse_s: float,
) -> float:
    dry_mass_kg = total_mass_kg - propellant_kg

    if propellant_kg <= 0.0 or dry_mass_kg <= 0.0 or specific_impulse_s <= 0.0:
        return 0.0

    return specific_impulse_s * STANDARD_GRAVITY_M_S2 * math.log(total_mass_kg / dry_mass_kg)


def calculate_oxygen_remaining_h(
    *,
    oxygen_kg: float,
    consumption_rate_kg_s: float,
) -> float | None:
    if consumption_rate_kg_s <= 0.0:
        return None

    return oxygen_kg / consumption_rate_kg_s / 3600.0


def calculate_power_remaining_h(
    *,
    battery_kwh: float,
    power_consumption_kw: float,
) -> float | None:
    if power_consumption_kw <= 0.0:
        return None

    return battery_kwh / power_consumption_kw


def calculate_fuel_flow_kg_s(
    *,
    engine_thrust_n: float,
    specific_impulse_s: float,
) -> float:
    if engine_thrust_n <= 0.0 or specific_impulse_s <= 0.0:
        return 0.0

    return engine_thrust_n / (specific_impulse_s * STANDARD_GRAVITY_M_S2)
