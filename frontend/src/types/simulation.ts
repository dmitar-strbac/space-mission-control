export type SimulationStatus =
  | "INITIALIZED"
  | "RUNNING"
  | "PAUSED"
  | "COMPLETED"
  | "FAILED";

export interface Vector2D {
  x: number;
  y: number;
}

export interface ManeuverExecution {
  id: string;
  sequence: number;
  maneuver_type: string;

  status:
    | "PENDING"
    | "ACTIVE"
    | "COMPLETED"
    | "CANCELLED"
    | "FAILED";

  delta_v_m_s: number;
  planned_offset_s: number;
  remaining_burn_s: number | null;
}

export interface SimulationState {
  position: Vector2D;
  velocity: Vector2D;

  total_mass_kg: number;
  propellant_mass_kg: number;
  elapsed_time_s: number;

  oxygen_kg: number;
  battery_kwh: number;

  maneuvers: ManeuverExecution[];
}

export interface Simulation {
  id: string;
  mission_id: string;
  trajectory_plan_id: string;
  vehicle_id: string;

  status: SimulationStatus;

  simulation_speed: number;
  integration_step_s: number;
  checkpoint_interval_s: number;

  initial_state_vector: Record<string, unknown>;
  planned_maneuvers: Array<Record<string, unknown>>;

  engine_thrust_n: number;
  engine_specific_impulse_s: number;

  oxygen_kg: number;
  oxygen_consumption_rate_kg_s: number;

  battery_kwh: number;
  power_consumption_kw: number;

  created_at: string;
  started_at: string | null;
  paused_at: string | null;
  completed_at: string | null;

  failure_reason: string | null;
}

export interface SimulationAdvanceResponse {
  simulated_duration_s: number;
  state: SimulationState;
}
