from smc_messaging import (
    EventBus,
    EventEnvelope,
    LiveSubject,
)

from app.core.config import get_settings
from app.domain.enums import ManeuverExecutionStatus
from app.domain.runtime import SimulationRuntime
from app.models.simulation_session import SimulationSession

settings = get_settings()


async def publish_simulation_state(
    *,
    event_bus: EventBus,
    simulation: SimulationSession,
    runtime: SimulationRuntime,
) -> None:
    initial_state = simulation.initial_state_vector

    initial_propellant_kg = float(
        initial_state.get(
            "propellant_mass_kg",
            runtime.state.propellant_mass_kg,
        )
    )

    active_maneuver = next(
        (
            maneuver
            for maneuver in runtime.maneuvers
            if maneuver.status is ManeuverExecutionStatus.ACTIVE
        ),
        None,
    )

    payload = {
        "mission_id": str(simulation.mission_id),
        "simulation_session_id": str(simulation.id),
        "simulation_time_s": runtime.state.elapsed_time_s,
        "position": {
            "x": runtime.state.position.x,
            "y": runtime.state.position.y,
        },
        "velocity": {
            "x": runtime.state.velocity.x,
            "y": runtime.state.velocity.y,
        },
        "total_mass_kg": runtime.state.total_mass_kg,
        "propellant_kg": runtime.state.propellant_mass_kg,
        "initial_propellant_kg": initial_propellant_kg,
        "oxygen_kg": runtime.oxygen_kg,
        "initial_oxygen_kg": simulation.oxygen_kg,
        "oxygen_consumption_rate_kg_s": (simulation.oxygen_consumption_rate_kg_s),
        "battery_kwh": runtime.battery_kwh,
        "initial_battery_kwh": simulation.battery_kwh,
        "power_consumption_kw": simulation.power_consumption_kw,
        "engine_thrust_n": (simulation.engine_thrust_n if active_maneuver is not None else 0.0),
        "engine_specific_impulse_s": (simulation.engine_specific_impulse_s),
        "active_maneuver_id": (str(active_maneuver.id) if active_maneuver is not None else None),
    }

    envelope = EventEnvelope.create(
        event_type=LiveSubject.SIMULATION_STATE_UPDATED.value,
        source=settings.service_name,
        correlation_id=str(simulation.mission_id),
        payload=payload,
    )

    await event_bus.publish_ephemeral(
        subject=LiveSubject.SIMULATION_STATE_UPDATED.value,
        envelope=envelope,
    )
