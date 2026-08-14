from datetime import UTC, datetime

from app.domain.telemetry import (
    calculate_altitude_km,
    calculate_fuel_flow_kg_s,
    calculate_oxygen_remaining_h,
    calculate_percentage,
    calculate_power_remaining_h,
    calculate_remaining_delta_v_m_s,
    calculate_speed_km_s,
    calculate_vertical_speed_m_s,
)
from app.schemas.communication import CommunicationStatusEventPayload
from app.schemas.simulation import SimulationStateEventPayload
from app.schemas.telemetry import (
    CommunicationTelemetry,
    LifeSupportTelemetry,
    NavigationTelemetry,
    PowerTelemetry,
    PropulsionTelemetry,
    TelemetryPoint,
)


class TelemetryService:
    def process_state(
        self,
        state: SimulationStateEventPayload,
        *,
        communication: (CommunicationStatusEventPayload | None) = None,
    ) -> TelemetryPoint:
        propellant_percent = calculate_percentage(
            current=state.propellant_kg,
            initial=state.initial_propellant_kg,
        )

        oxygen_percent = calculate_percentage(
            current=state.oxygen_kg,
            initial=state.initial_oxygen_kg,
        )

        battery_percent = calculate_percentage(
            current=state.battery_kwh,
            initial=state.initial_battery_kwh,
        )

        communication_telemetry = None

        if communication is not None:
            communication_telemetry = CommunicationTelemetry(
                signal_status=(communication.signal_status),
                one_way_delay_ms=(communication.one_way_delay_ms),
                packet_loss_percent=(communication.packet_loss_percent),
                last_contact_at=(
                    communication.observed_at if communication.signal_status != "LOST" else None
                ),
            )

        return TelemetryPoint(
            mission_id=state.mission_id,
            simulation_session_id=(state.simulation_session_id),
            simulation_time_s=(state.simulation_time_s),
            recorded_at=datetime.now(UTC),
            navigation=NavigationTelemetry(
                altitude_km=calculate_altitude_km(
                    position_x_m=state.position.x,
                    position_y_m=state.position.y,
                ),
                speed_km_s=calculate_speed_km_s(
                    velocity_x_m_s=state.velocity.x,
                    velocity_y_m_s=state.velocity.y,
                ),
                vertical_speed_m_s=(
                    calculate_vertical_speed_m_s(
                        position_x_m=state.position.x,
                        position_y_m=state.position.y,
                        velocity_x_m_s=state.velocity.x,
                        velocity_y_m_s=state.velocity.y,
                    )
                ),
            ),
            propulsion=PropulsionTelemetry(
                propellant_kg=state.propellant_kg,
                propellant_percent=(propellant_percent),
                fuel_flow_kg_s=(
                    calculate_fuel_flow_kg_s(
                        engine_thrust_n=(state.engine_thrust_n),
                        specific_impulse_s=(state.engine_specific_impulse_s),
                    )
                ),
                engine_thrust_n=(state.engine_thrust_n),
                remaining_delta_v_m_s=(
                    calculate_remaining_delta_v_m_s(
                        total_mass_kg=(state.total_mass_kg),
                        propellant_kg=(state.propellant_kg),
                        specific_impulse_s=(state.engine_specific_impulse_s),
                    )
                ),
            ),
            life_support=LifeSupportTelemetry(
                oxygen_kg=state.oxygen_kg,
                oxygen_percent=oxygen_percent,
                crew_consumption_rate_kg_s=(state.oxygen_consumption_rate_kg_s),
                estimated_oxygen_remaining_h=(
                    calculate_oxygen_remaining_h(
                        oxygen_kg=state.oxygen_kg,
                        consumption_rate_kg_s=(state.oxygen_consumption_rate_kg_s),
                    )
                ),
            ),
            power=PowerTelemetry(
                battery_kwh=state.battery_kwh,
                battery_percent=battery_percent,
                power_consumption_kw=(state.power_consumption_kw),
                estimated_power_remaining_h=(
                    calculate_power_remaining_h(
                        battery_kwh=state.battery_kwh,
                        power_consumption_kw=(state.power_consumption_kw),
                    )
                ),
            ),
            communication=communication_telemetry,
        )
