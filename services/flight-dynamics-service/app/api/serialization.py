from app.domain.runtime import SimulationRuntime
from app.schemas.simulation import (
    ManeuverExecutionResponse,
    SimulationStateResponse,
    Vector2DSchema,
)


def simulation_state_response(
    runtime: SimulationRuntime,
) -> SimulationStateResponse:
    state = runtime.state

    return SimulationStateResponse(
        position=Vector2DSchema(
            x=state.position.x,
            y=state.position.y,
        ),
        velocity=Vector2DSchema(
            x=state.velocity.x,
            y=state.velocity.y,
        ),
        total_mass_kg=state.total_mass_kg,
        propellant_mass_kg=(state.propellant_mass_kg),
        elapsed_time_s=state.elapsed_time_s,
        oxygen_kg=runtime.oxygen_kg,
        battery_kwh=runtime.battery_kwh,
        maneuvers=[
            ManeuverExecutionResponse(
                id=maneuver.id,
                sequence=maneuver.sequence,
                maneuver_type=maneuver.maneuver_type,
                status=maneuver.status,
                delta_v_m_s=maneuver.delta_v_m_s,
                planned_offset_s=(maneuver.planned_offset_s),
                remaining_burn_s=(maneuver.remaining_burn_s),
            )
            for maneuver in runtime.maneuvers
        ],
    )
