export type ReferenceFrame =
  "EARTH_CENTERED_INERTIAL";

export type TrajectoryStatus =
  | "PLANNED"
  | "INFEASIBLE"
  | "SUPERSEDED";

export type ManeuverType =
  | "ORBIT_INSERTION"
  | "ORBIT_RAISE"
  | "ORBIT_LOWER"
  | "MIDCOURSE_CORRECTION"
  | "DEORBIT_BURN";

export type ManeuverStatus =
  | "PLANNED"
  | "CANCELLED";

export interface Maneuver {
  id: string;
  sequence: number;
  maneuver_type: ManeuverType;
  delta_v_m_s: number;
  planned_offset_s: number;
  status: ManeuverStatus;
}

export interface TrajectoryPlan {
  id: string;
  mission_id: string;

  reference_frame: ReferenceFrame;

  departure_time: string;
  arrival_time: string;

  initial_state_vector: Record<string, unknown>;
  target_state_vector: Record<string, unknown>;

  required_delta_v_m_s: number;
  estimated_propellant_kg: number;
  propellant_reserve_percent: number;
  safety_margin_percent: number;
  window_score: number;

  status: TrajectoryStatus;
  created_at: string;

  maneuvers: Maneuver[];
}
