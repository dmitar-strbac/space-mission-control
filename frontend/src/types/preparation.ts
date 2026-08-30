export type SagaStepType =
  | "VEHICLE_RESERVATION"
  | "TRAJECTORY_PLANNING"
  | "RESOURCE_VALIDATION"
  | "COMMUNICATION_PROFILE"
  | "SIMULATION_INITIALIZATION";

export type SagaStepStatus =
  | "PENDING"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "FAILED"
  | "COMPENSATING"
  | "COMPENSATED";

export interface SagaStep {
  id: string;
  saga_id: string;
  mission_id: string;

  step_type: SagaStepType;
  status: SagaStepStatus;

  failure_reason: string | null;

  started_at: string | null;
  completed_at: string | null;
  failed_at: string | null;
  compensated_at: string | null;
}

export interface MissionPreparation {
  mission_id: string;
  saga_id: string | null;
  steps: SagaStep[];
}
