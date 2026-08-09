from math import exp, isfinite, log

from orbital_mechanics.constants import STANDARD_GRAVITY_M_S2
from orbital_mechanics.models import EngineParameters, ThrustCommand, Vector2D


def mass_flow_rate_kg_s(
    engine: EngineParameters,
    throttle: float = 1.0,
) -> float:
    _validate_throttle(throttle)

    effective_thrust_n = engine.thrust_n * throttle

    return effective_thrust_n / (engine.specific_impulse_s * STANDARD_GRAVITY_M_S2)


def available_delta_v_m_s(
    total_mass_kg: float,
    propellant_mass_kg: float,
    specific_impulse_s: float,
) -> float:
    _validate_mass_values(
        total_mass_kg=total_mass_kg,
        propellant_mass_kg=propellant_mass_kg,
    )

    if not isfinite(specific_impulse_s) or specific_impulse_s <= 0.0:
        raise ValueError("Specific impulse must be a positive finite number.")

    if propellant_mass_kg == 0.0:
        return 0.0

    final_mass_kg = total_mass_kg - propellant_mass_kg

    if final_mass_kg <= 0.0:
        raise ValueError("Dry spacecraft mass must be greater than zero.")

    exhaust_velocity_m_s = specific_impulse_s * STANDARD_GRAVITY_M_S2

    return exhaust_velocity_m_s * log(total_mass_kg / final_mass_kg)


def propellant_consumed_kg(
    engine: EngineParameters,
    burn_duration_s: float,
    available_propellant_kg: float,
    throttle: float = 1.0,
) -> float:
    if not isfinite(burn_duration_s) or burn_duration_s < 0.0:
        raise ValueError("Burn duration must be a non-negative finite number.")

    if not isfinite(available_propellant_kg) or available_propellant_kg < 0.0:
        raise ValueError("Available propellant must be a non-negative finite number.")

    requested_propellant_kg = (
        mass_flow_rate_kg_s(engine=engine, throttle=throttle) * burn_duration_s
    )

    return min(requested_propellant_kg, available_propellant_kg)


def thrust_acceleration_m_s2(
    command: ThrustCommand,
    engine: EngineParameters,
    total_mass_kg: float,
) -> Vector2D:
    if not isfinite(total_mass_kg) or total_mass_kg <= 0.0:
        raise ValueError("Total spacecraft mass must be a positive finite number.")

    effective_thrust_n = engine.thrust_n * command.throttle
    acceleration_m_s2 = effective_thrust_n / total_mass_kg

    return command.normalized_direction * acceleration_m_s2


def required_propellant_mass_kg(
    total_mass_kg: float,
    required_delta_v_m_s: float,
    specific_impulse_s: float,
) -> float:
    if not isfinite(total_mass_kg) or total_mass_kg <= 0.0:
        raise ValueError("Total spacecraft mass must be a positive finite number.")

    if not isfinite(required_delta_v_m_s) or required_delta_v_m_s < 0.0:
        raise ValueError("Required delta-v must be a non-negative finite number.")

    if not isfinite(specific_impulse_s) or specific_impulse_s <= 0.0:
        raise ValueError("Specific impulse must be a positive finite number.")

    if required_delta_v_m_s == 0.0:
        return 0.0

    exhaust_velocity_m_s = specific_impulse_s * STANDARD_GRAVITY_M_S2
    final_mass_kg = total_mass_kg / exp(required_delta_v_m_s / exhaust_velocity_m_s)

    return total_mass_kg - final_mass_kg


def _validate_mass_values(
    total_mass_kg: float,
    propellant_mass_kg: float,
) -> None:
    if not isfinite(total_mass_kg) or total_mass_kg <= 0.0:
        raise ValueError("Total spacecraft mass must be a positive finite number.")

    if not isfinite(propellant_mass_kg) or propellant_mass_kg < 0.0:
        raise ValueError("Propellant mass must be a non-negative finite number.")

    if propellant_mass_kg > total_mass_kg:
        raise ValueError("Propellant mass cannot exceed total spacecraft mass.")


def _validate_throttle(throttle: float) -> None:
    if not isfinite(throttle):
        raise ValueError("Throttle must be a finite number.")

    if not 0.0 <= throttle <= 1.0:
        raise ValueError("Throttle must be between zero and one.")
