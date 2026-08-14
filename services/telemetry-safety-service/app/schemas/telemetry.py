from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NavigationTelemetry(BaseModel):
    altitude_km: float

    distance_from_target_km: float | None = None

    speed_km_s: float = Field(
        ge=0,
    )

    vertical_speed_m_s: float

    trajectory_deviation_km: float | None = None

    estimated_arrival_time: datetime | None = None


class PropulsionTelemetry(BaseModel):
    propellant_kg: float = Field(
        ge=0,
    )
    propellant_percent: float = Field(
        ge=0,
        le=100,
    )

    fuel_flow_kg_s: float = Field(
        ge=0,
    )

    engine_thrust_n: float = Field(
        ge=0,
    )

    remaining_delta_v_m_s: float = Field(
        ge=0,
    )


class LifeSupportTelemetry(BaseModel):
    oxygen_kg: float = Field(
        ge=0,
    )

    oxygen_percent: float = Field(
        ge=0,
        le=100,
    )

    crew_consumption_rate_kg_s: float = Field(
        ge=0,
    )

    estimated_oxygen_remaining_h: float | None


class PowerTelemetry(BaseModel):
    battery_kwh: float = Field(
        ge=0,
    )

    battery_percent: float = Field(
        ge=0,
        le=100,
    )

    power_generation_kw: float | None = None

    power_consumption_kw: float = Field(
        ge=0,
    )

    estimated_power_remaining_h: float | None


class CommunicationTelemetry(BaseModel):
    signal_status: str

    one_way_delay_ms: float = Field(
        ge=0,
    )

    packet_loss_percent: float = Field(
        ge=0,
        le=100,
    )

    last_contact_at: datetime | None


class TelemetryPoint(BaseModel):
    mission_id: UUID
    simulation_session_id: UUID

    simulation_time_s: float = Field(
        ge=0,
    )

    recorded_at: datetime

    navigation: NavigationTelemetry
    propulsion: PropulsionTelemetry
    life_support: LifeSupportTelemetry
    power: PowerTelemetry

    communication: CommunicationTelemetry | None = None
