import type {
  Mission,
  MissionCreateRequest,
  MissionEvent,
  MissionListResponse,
} from "../types/mission";
import type { MissionPreparation } from "../types/preparation";
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

export function prepareMission(
  missionId: string,
): Promise<Mission> {
  return apiRequest<Mission>(
    `/api/mission/missions/${missionId}/prepare`,
    {
      method: "POST",
    },
  );
}

export function getMissionPreparation(
  missionId: string,
): Promise<MissionPreparation> {
  return apiRequest<MissionPreparation>(
    `/api/mission/missions/${missionId}/preparation`,
  );
}

export function launchMission(
  missionId: string,
): Promise<Mission> {
  return apiRequest<Mission>(
    `/api/mission/missions/${missionId}/launch`,
    {
      method: "POST",
    },
  );
}

export function getMissionTimeline(
  missionId: string,
): Promise<MissionEvent[]> {
  return apiRequest<MissionEvent[]>(
    `/api/mission/missions/${missionId}/timeline`,
  );
}

export function abortMission(
  missionId: string,
): Promise<Mission> {
  return apiRequest<Mission>(
    `/api/mission/missions/${missionId}/abort`,
    {
      method: "POST",
    },
  );
}
