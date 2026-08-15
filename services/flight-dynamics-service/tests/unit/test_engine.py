from uuid import uuid4

import pytest

from app.domain.engine import (
    SimulationConfiguration,
    advance_runtime,
)
from app.domain.enums import (
    ManeuverExecutionStatus,
    ManeuverType,
)
from app.domain.faults import (
    ActiveFault,
    FaultType,
)
from app.domain.runtime import (
    RuntimeManeuver,
    SimulationRuntime,
)
from orbital_mechanics.models import EngineParameters
from orbital_mechanics.orbits import create_circular_orbit_state


def _runtime() -> SimulationRuntime:
    return SimulationRuntime(
        state=create_circular_orbit_state(
            altitude_m=400_000.0,
            total_mass_kg=10_000.0,
            propellant_mass_kg=2_000.0,
        ),
        oxygen_kg=5.0,
        battery_kwh=10.0,
    )


def _configuration() -> SimulationConfiguration:
    return SimulationConfiguration(
        engine=EngineParameters(
            thrust_n=100_000.0,
            specific_impulse_s=450.0,
        ),
        integration_step_s=0.25,
        oxygen_consumption_rate_kg_s=0.01,
        power_consumption_kw=3.6,
    )


def test_coast_propagates_state_without_consuming_propellant() -> None:
    runtime = _runtime()

    initial_position = runtime.state.position
    initial_propellant = runtime.state.propellant_mass_kg
    initial_mass = runtime.state.total_mass_kg

    advance_runtime(
        runtime=runtime,
        configuration=_configuration(),
        simulated_duration_s=10.0,
    )

    assert runtime.state.elapsed_time_s == pytest.approx(10.0)
    assert runtime.state.position != initial_position

    assert runtime.state.propellant_mass_kg == pytest.approx(initial_propellant)
    assert runtime.state.total_mass_kg == pytest.approx(initial_mass)


def test_operational_resources_are_consumed_during_coast() -> None:
    runtime = _runtime()

    advance_runtime(
        runtime=runtime,
        configuration=_configuration(),
        simulated_duration_s=10.0,
    )

    assert runtime.oxygen_kg == pytest.approx(4.9)
    assert runtime.battery_kwh == pytest.approx(9.99)


def test_orbit_raise_maneuver_consumes_propellant_and_mass() -> None:
    runtime = _runtime()

    maneuver = RuntimeManeuver(
        id=uuid4(),
        sequence=1,
        maneuver_type=ManeuverType.ORBIT_RAISE,
        delta_v_m_s=10.0,
        planned_offset_s=0.0,
    )

    runtime.maneuvers.append(maneuver)

    initial_mass = runtime.state.total_mass_kg
    initial_propellant = runtime.state.propellant_mass_kg

    advance_runtime(
        runtime=runtime,
        configuration=_configuration(),
        simulated_duration_s=2.0,
    )

    assert maneuver.status is ManeuverExecutionStatus.COMPLETED

    assert runtime.state.total_mass_kg < initial_mass
    assert runtime.state.propellant_mass_kg < initial_propellant

    assert runtime.state.elapsed_time_s == pytest.approx(2.0)


def test_maneuver_waits_until_planned_offset() -> None:
    runtime = _runtime()

    maneuver = RuntimeManeuver(
        id=uuid4(),
        sequence=1,
        maneuver_type=ManeuverType.ORBIT_RAISE,
        delta_v_m_s=10.0,
        planned_offset_s=5.0,
    )

    runtime.maneuvers.append(maneuver)

    advance_runtime(
        runtime=runtime,
        configuration=_configuration(),
        simulated_duration_s=4.0,
    )

    assert maneuver.status is ManeuverExecutionStatus.PENDING

    advance_runtime(
        runtime=runtime,
        configuration=_configuration(),
        simulated_duration_s=2.0,
    )

    assert maneuver.status is ManeuverExecutionStatus.COMPLETED
    assert runtime.state.elapsed_time_s == pytest.approx(6.0)


def test_orbit_lower_uses_retrograde_burn() -> None:
    runtime = _runtime()

    initial_speed = runtime.state.speed_m_s

    runtime.maneuvers.append(
        RuntimeManeuver(
            id=uuid4(),
            sequence=1,
            maneuver_type=ManeuverType.ORBIT_LOWER,
            delta_v_m_s=10.0,
            planned_offset_s=0.0,
        )
    )

    advance_runtime(
        runtime=runtime,
        configuration=_configuration(),
        simulated_duration_s=1.0,
    )

    assert runtime.state.speed_m_s < initial_speed


def test_maneuver_fails_when_propellant_is_insufficient() -> None:
    runtime = SimulationRuntime(
        state=create_circular_orbit_state(
            altitude_m=400_000.0,
            total_mass_kg=10_000.0,
            propellant_mass_kg=1.0,
        ),
        oxygen_kg=5.0,
        battery_kwh=10.0,
        maneuvers=[
            RuntimeManeuver(
                id=uuid4(),
                sequence=1,
                maneuver_type=ManeuverType.ORBIT_RAISE,
                delta_v_m_s=1_000.0,
                planned_offset_s=0.0,
            )
        ],
    )

    with pytest.raises(
        ValueError,
        match="Insufficient propellant",
    ):
        advance_runtime(
            runtime=runtime,
            configuration=_configuration(),
            simulated_duration_s=1.0,
        )

    assert runtime.maneuvers[0].status is ManeuverExecutionStatus.FAILED


def test_advance_uses_fixed_integration_steps() -> None:
    runtime = _runtime()

    advance_runtime(
        runtime=runtime,
        configuration=_configuration(),
        simulated_duration_s=2.5,
    )

    assert runtime.state.elapsed_time_s == pytest.approx(2.5)


def test_power_failure_increases_battery_consumption() -> None:
    runtime = _runtime()

    runtime.active_faults[FaultType.POWER_FAILURE] = ActiveFault(
        fault_type=FaultType.POWER_FAILURE,
        magnitude=5.0,
    )

    configuration = _configuration()

    initial_battery = runtime.battery_kwh

    advance_runtime(
        runtime=runtime,
        configuration=configuration,
        simulated_duration_s=3600.0,
    )

    expected_consumption_kwh = configuration.power_consumption_kw + 5.0

    assert runtime.battery_kwh == pytest.approx(
        max(
            initial_battery - expected_consumption_kwh,
            0.0,
        )
    )
