import type {
  Maneuver,
  TrajectoryPlan,
} from "../types/trajectory";
import { apiRequest } from "./apiClient";

export function getTrajectoryPlan(
  missionId: string,
): Promise<TrajectoryPlan> {
  return apiRequest<TrajectoryPlan>(
    `/api/trajectory/trajectories/${missionId}`,
  );
}

export function getTrajectoryManeuvers(
  missionId: string,
): Promise<Maneuver[]> {
  return apiRequest<Maneuver[]>(
    `/api/trajectory/trajectories/${missionId}/maneuvers`,
  );
}
