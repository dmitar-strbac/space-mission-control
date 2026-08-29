export type TelemetrySocketStatus =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

export interface NavigationTelemetry {
  altitude_km: number;
  distance_from_target_km: number | null;
  speed_km_s: number;
  vertical_speed_m_s: number;
  trajectory_deviation_km: number | null;
  estimated_arrival_time: string | null;
}

export interface PropulsionTelemetry {
  propellant_kg: number;
  propellant_percent: number;
  fuel_flow_kg_s: number;
  engine_thrust_n: number;
  remaining_delta_v_m_s: number;
}

export interface LifeSupportTelemetry {
  oxygen_kg: number;
  oxygen_percent: number;
  crew_consumption_rate_kg_s: number;
  estimated_oxygen_remaining_h: number | null;
}

export interface PowerTelemetry {
  battery_kwh: number;
  battery_percent: number;
  power_generation_kw: number | null;
  power_consumption_kw: number;
  estimated_power_remaining_h: number | null;
}

export interface CommunicationTelemetry {
  signal_status: string;
  one_way_delay_ms: number;
  packet_loss_percent: number;
  last_contact_at: string | null;
}

export interface TelemetryPoint {
  mission_id: string;
  simulation_session_id: string;
  simulation_time_s: number;
  recorded_at: string;

  navigation: NavigationTelemetry;
  propulsion: PropulsionTelemetry;
  life_support: LifeSupportTelemetry;
  power: PowerTelemetry;

  communication: CommunicationTelemetry | null;
}

export type AlertSeverity =
  | "INFO"
  | "CAUTION"
  | "WARNING"
  | "CRITICAL";

export type AlertType =
  | "LOW_PROPELLANT"
  | "PROPELLANT_RESERVE_VIOLATION"
  | "OXYGEN_LOW"
  | "OXYGEN_CRITICAL"
  | "POWER_LOW"
  | "TRAJECTORY_DEVIATION"
  | "COMMUNICATION_DEGRADED"
  | "COMMUNICATION_LOST";

export interface MissionAlert {
  id: string;
  mission_id: string;

  alert_type: AlertType;
  severity: AlertSeverity;

  message: string;

  measured_value: number | string;
  threshold: number | string;

  created_at: string;
  last_seen_at: string;

  resolved_at: string | null;
}

export type TelemetrySocketMessage =
  | {
      type: "telemetry";
      data: TelemetryPoint;
    }
  | {
      type: "alert";
      data: MissionAlert;
    };
