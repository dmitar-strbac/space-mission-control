import type {
  Mission,
  MissionCreateRequest,
  MissionEvent,
  MissionListResponse,
} from "../types/mission";
import { apiRequest } from "./apiClient";

interface MissionListParameters {
  limit?: number;
  offset?: number;
}

export function getMissions(
  parameters: MissionListParameters = {},
): Promise<MissionListResponse> {
  const {
    limit = 20,
    offset = 0,
  } = parameters;

  return apiRequest<MissionListResponse>(
    `/api/mission/missions?limit=${limit}&offset=${offset}`,
  );
}

export function getMission(
  missionId: string,
): Promise<Mission> {
  return apiRequest<Mission>(
    `/api/mission/missions/${missionId}`,
  );
}

export function createMission(
  request: MissionCreateRequest,
): Promise<Mission> {
  return apiRequest<Mission>("/api/mission/missions", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export function getMissionTimeline(
  missionId: string,
): Promise<MissionEvent[]> {
  return apiRequest<MissionEvent[]>(
    `/api/mission/missions/${missionId}/timeline`,
  );
}
