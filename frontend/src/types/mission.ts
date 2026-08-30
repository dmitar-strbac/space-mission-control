export type MissionType =
  | "LEO"
  | "LEO_RENDEZVOUS"
  | "LUNAR";

export type MissionStatus =
  | "DRAFT"
  | "PLANNING"
  | "PREPARING"
  | "READY"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "ABORTING"
  | "ABORTED"
  | "FAILED_PREPARATION"
  | "FAILED";

export type MissionPhase =
  | "ORBIT_INSERTION"
  | "ORBIT_COAST"
  | "ORBIT_MAINTENANCE"
  | "RENDEZVOUS_APPROACH"
  | "TRANSLUNAR_COAST"
  | "LUNAR_ORBIT_INSERTION"
  | "DESCENT"
  | "RETURN_TRANSFER"
  | "DEORBIT";

export interface Mission {
  id: string;
  name: string;
  mission_type: MissionType;
  status: MissionStatus;
  mission_phase: MissionPhase | null;
  vehicle_id: string | null;
  crew_count: number;
  target_type: string;
  target_parameters: Record<string, unknown>;
  planned_launch_time: string | null;
  simulation_speed: number;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  failure_reason: string | null;
}

export interface MissionListResponse {
  items: Mission[];
  total: number;
  limit: number;
  offset: number;
}

export interface MissionCreateRequest {
  name: string;
  mission_type: MissionType;
  vehicle_id: string | null;
  crew_count: number;
  target_type: string;
  target_parameters: Record<string, unknown>;
  planned_launch_time: string | null;
  simulation_speed: number;
}

export type MissionEventType =
  | "MISSION_CREATED"
  | "PREPARATION_REQUESTED"
  | "PREPARATION_FAILED"
  | "STATUS_CHANGED"
  | "PHASE_CHANGED"
  | "MISSION_STARTED"
  | "ABORT_REQUESTED"
  | "MISSION_ABORTED"
  | "MISSION_COMPLETED"
  | "MISSION_FAILED";

export interface MissionEvent {
  id: string;
  mission_id: string;
  event_type: MissionEventType;
  source: string;
  payload: Record<string, unknown>;
  occurred_at: string;
}
