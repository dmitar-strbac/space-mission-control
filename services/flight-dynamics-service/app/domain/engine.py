from dataclasses import dataclass

from app.domain.enums import (
    ManeuverExecutionStatus,
    ManeuverType,
)
from app.domain.runtime import (
    RuntimeManeuver,
    SimulationRuntime,
)
from orbital_mechanics.dynamics import create_dynamics_function
from orbital_mechanics.integrators.rk4 import rk4_step
from orbital_mechanics.models import (
    EngineParameters,
    StateVector,
    ThrustCommand,
    Vector2D,
)
from orbital_mechanics.propulsion import (
    mass_flow_rate_kg_s,
    required_propellant_mass_kg,
)


@dataclass(frozen=True, slots=True)
class SimulationConfiguration:
    engine: EngineParameters

    integration_step_s: float

    oxygen_consumption_rate_kg_s: float
    power_consumption_kw: float


def advance_runtime(
    *,
    runtime: SimulationRuntime,
    configuration: SimulationConfiguration,
    simulated_duration_s: float,
) -> None:
    remaining_duration_s = simulated_duration_s

    while remaining_duration_s > 0.0:
        step_s = min(
            configuration.integration_step_s,
            remaining_duration_s,
        )

        _advance_step(
            runtime=runtime,
            configuration=configuration,
            time_step_s=step_s,
        )

        remaining_duration_s -= step_s


def _advance_step(
    *,
    runtime: SimulationRuntime,
    configuration: SimulationConfiguration,
    time_step_s: float,
) -> None:
    remaining_step_s = time_step_s

    while remaining_step_s > 0.0:
        active = _get_active_maneuver(runtime)

        if active is not None:
            burn_step_s = min(
                remaining_step_s,
                active.remaining_burn_s or 0.0,
            )

            if burn_step_s <= 0.0:
                _complete_maneuver(active)
                continue

            _propagate_with_maneuver(
                runtime=runtime,
                configuration=configuration,
                maneuver=active,
                time_step_s=burn_step_s,
            )

            active.remaining_burn_s = max(
                (active.remaining_burn_s or 0.0) - burn_step_s,
                0.0,
            )

            if active.remaining_burn_s <= 1e-9:
                _complete_maneuver(active)

            remaining_step_s -= burn_step_s
            continue

        pending = _get_next_pending_maneuver(runtime)

        if pending is not None:
            time_until_maneuver_s = pending.planned_offset_s - runtime.state.elapsed_time_s

            if time_until_maneuver_s <= 1e-9:
                _activate_maneuver(
                    runtime=runtime,
                    maneuver=pending,
                    configuration=configuration,
                )
                continue

            coast_step_s = min(
                remaining_step_s,
                time_until_maneuver_s,
            )
        else:
            coast_step_s = remaining_step_s

        _propagate_coast(
            runtime=runtime,
            time_step_s=coast_step_s,
        )

        _consume_operational_resources(
            runtime=runtime,
            configuration=configuration,
            time_step_s=coast_step_s,
        )

        remaining_step_s -= coast_step_s


def _propagate_coast(
    *,
    runtime: SimulationRuntime,
    time_step_s: float,
) -> None:
    derivative = create_dynamics_function()

    runtime.state = rk4_step(
        state=runtime.state,
        time_step_s=time_step_s,
        derivative_function=derivative,
    )


def _propagate_with_maneuver(
    *,
    runtime: SimulationRuntime,
    configuration: SimulationConfiguration,
    maneuver: RuntimeManeuver,
    time_step_s: float,
) -> None:
    direction = _resolve_thrust_direction(
        state=runtime.state,
        maneuver=maneuver,
    )

    command = ThrustCommand(
        direction=direction,
        throttle=1.0,
    )

    derivative = create_dynamics_function(
        engine=configuration.engine,
        thrust_command=command,
    )

    runtime.state = rk4_step(
        state=runtime.state,
        time_step_s=time_step_s,
        derivative_function=derivative,
    )

    _consume_operational_resources(
        runtime=runtime,
        configuration=configuration,
        time_step_s=time_step_s,
    )


def _activate_maneuver(
    *,
    runtime: SimulationRuntime,
    maneuver: RuntimeManeuver,
    configuration: SimulationConfiguration,
) -> None:
    required_propellant_kg = required_propellant_mass_kg(
        total_mass_kg=runtime.state.total_mass_kg,
        required_delta_v_m_s=maneuver.delta_v_m_s,
        specific_impulse_s=(configuration.engine.specific_impulse_s),
    )

    if required_propellant_kg > runtime.state.propellant_mass_kg:
        maneuver.status = ManeuverExecutionStatus.FAILED

        raise ValueError("Insufficient propellant for planned maneuver.")

    mass_flow_kg_s = mass_flow_rate_kg_s(
        engine=configuration.engine,
    )

    maneuver.remaining_burn_s = required_propellant_kg / mass_flow_kg_s

    maneuver.status = ManeuverExecutionStatus.ACTIVE


def _complete_maneuver(
    maneuver: RuntimeManeuver,
) -> None:
    maneuver.remaining_burn_s = 0.0
    maneuver.status = ManeuverExecutionStatus.COMPLETED


def _get_active_maneuver(
    runtime: SimulationRuntime,
) -> RuntimeManeuver | None:
    return next(
        (
            maneuver
            for maneuver in runtime.maneuvers
            if maneuver.status is ManeuverExecutionStatus.ACTIVE
        ),
        None,
    )


def _get_next_pending_maneuver(
    runtime: SimulationRuntime,
) -> RuntimeManeuver | None:
    pending = [
        maneuver
        for maneuver in runtime.maneuvers
        if maneuver.status is ManeuverExecutionStatus.PENDING
    ]

    if not pending:
        return None

    return min(
        pending,
        key=lambda item: (
            item.planned_offset_s,
            item.sequence,
        ),
    )


def _resolve_thrust_direction(
    *,
    state: StateVector,
    maneuver: RuntimeManeuver,
) -> Vector2D:
    if maneuver.direction is not None:
        return maneuver.direction.normalized()

    prograde = state.velocity.normalized()

    if maneuver.maneuver_type in {
        ManeuverType.ORBIT_INSERTION,
        ManeuverType.ORBIT_RAISE,
        ManeuverType.MIDCOURSE_CORRECTION,
    }:
        return prograde

    if maneuver.maneuver_type in {
        ManeuverType.ORBIT_LOWER,
        ManeuverType.DEORBIT_BURN,
    }:
        return prograde * -1.0

    raise ValueError(f"Unsupported maneuver type: {maneuver.maneuver_type.value}")


def _consume_operational_resources(
    *,
    runtime: SimulationRuntime,
    configuration: SimulationConfiguration,
    time_step_s: float,
) -> None:
    oxygen_consumed_kg = configuration.oxygen_consumption_rate_kg_s * time_step_s

    runtime.oxygen_kg = max(
        runtime.oxygen_kg - oxygen_consumed_kg,
        0.0,
    )

    battery_consumed_kwh = configuration.power_consumption_kw * time_step_s / 3600.0

    runtime.battery_kwh = max(
        runtime.battery_kwh - battery_consumed_kwh,
        0.0,
    )
